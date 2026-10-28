"""Experimental enrollment-indexed matcher; independent-session validation pending.

Parameters were explored on the historical development cohort. Passing its
repeated splits is a regression check, not independent accuracy evidence.
"""
from dataclasses import dataclass, field
import threading
import cv2
import numpy as np
from demo_matcher import FastCCDemoMatcher
from fastcc_accelerated import AcceleratedFastCC
from pose_matcher import FastCCPoseMatcher
from registered_matcher import local_features, registration
from pklnet_roi import normalize_roi_pixels


@dataclass
class IndexedProbe:
    bank: np.ndarray
    source: np.ndarray
    native: np.ndarray
    views: list = field(default_factory=list)
    route: str = 'pose'
    legacy: tuple | None = None


class IndexedDemoMatcher(FastCCDemoMatcher):
    name = 'FastCCIndexed-v7-experimental'
    magic = FastCCDemoMatcher.magic + 1
    enrollment_requires_hypotheses = True
    prepared_cache_limit_bytes = 256 * 1024 * 1024

    def __init__(self, base):
        super().__init__(AcceleratedFastCC(base))
        self._pose = FastCCPoseMatcher(self.base)
        self._index_lock = threading.RLock()
        self._index_key = None
        self._index = None
        self._references = None

    def extract_probe_with_context(self, full, quad, normalized_roi):
        q = np.asarray(quad, np.float32)
        if q.shape != (4, 2) or not np.isfinite(q).all():
            raise ValueError('Invalid palm quadrilateral')
        bank = self._pose.extract_with_context(full, q, normalized_roi)
        dst = np.asarray([[384,0],[0,0],[0,384],[384,384]] if self.geometry.isAntiClock(q[:3].reshape(-1))
                         else [[0,0],[384,0],[384,384],[0,384]], np.float32)
        gray = cv2.cvtColor(np.asarray(full.convert('RGB')), cv2.COLOR_RGB2GRAY)
        return IndexedProbe(bank, cv2.getPerspectiveTransform(q, dst), gray)

    def prepare_probe(self, feature):
        if not isinstance(feature, IndexedProbe):
            raise ValueError('Indexed matcher requires a fresh query image')
        return feature

    def prepare_enrollment(self, features):
        prepared = []
        for feature in features:
            q = self._unpack(feature)
            if q[3] is None or not q[-1]:
                raise ValueError('Indexed enrollment requires complete candidate features')
            codes, views = {}, []
            for sigma, source, points, descriptors in q[-1]:
                key = source.tobytes()
                if key not in codes:
                    pixels = normalize_roi_pixels(cv2.warpPerspective(q[3], np.diag([1/3,1/3,1])@source, (128,128)))
                    codes[key] = self.base.extract(pixels)
                views.append((sigma, source.copy(), points.copy(), descriptors.copy(), codes[key]))
            target = (q[1][0].copy(), None, None, q[1][3], q[1][4].copy(), q[1][5].copy())
            secondary = tuple(x.copy() for x in q[2])
            prepared.append((q[1][0][0].copy().astype(bool), views, (target, secondary)))
        return prepared

    @staticmethod
    def prepared_bytes(value):
        seen = set()
        def size(v):
            if id(v) in seen: return 0
            seen.add(id(v))
            if isinstance(v, np.ndarray): return v.nbytes
            if isinstance(v, (tuple, list)): return sum(size(x) for x in v)
            return 0
        return size(value)

    def prepare_gallery(self, groups):
        # Strong references prevent object-ID reuse while an index is cached.
        key = tuple((user, id(samples)) for user, samples in sorted(groups.items()))
        with self._index_lock:
            if key == self._index_key: return
            descriptors, labels, mapping, positions = [], [], [], {}
            for user, samples in sorted(groups.items()):
                for sample, prepared in enumerate(samples):
                    views = prepared[1]
                    positions[(user, sample)] = []
                    for view_index, view in enumerate(views):
                        if len(view[3]) < 4: continue
                        group = len(mapping)
                        mapping.append((user, sample, view_index))
                        positions[(user, sample)].append(group)
                        descriptors.append(view[3])
                        labels.append(np.full(len(view[3]), group, np.int32))
            packed = np.concatenate(descriptors) if descriptors else np.empty((0,128), np.float32)
            if packed.nbytes > 256*1024*1024:
                raise ValueError('Experimental descriptor index exceeds 256 MiB')
            index = None
            if len(packed) >= 16:
                cv2.setRNGSeed(20261028)
                index = cv2.FlannBasedMatcher(dict(algorithm=1, trees=4), dict(checks=64))
                index.add([packed]); index.train()
            self._index = index
            self._labels = np.concatenate(labels) if labels else np.empty(0, np.int32)
            self._mapping, self._positions = mapping, positions
            self._references, self._index_key = dict(groups), key

    @staticmethod
    def _aggregate(pair_scores):
        return float(np.mean(sorted(pair_scores)[:2]))

    def _query_views(self, probe):
        if probe.views: return probe.views
        # Two normal-context and two wider-field views; original pixels remain
        # available for the final aligned 128x128 score in both cases.
        specs = [(1.,192.,192.), (.5,288.,576.)]
        def extract(spec):
            scale, offset, unoffset = spec
            transform = np.asarray([[scale,0,offset],[0,scale,offset],[0,0,1.]])
            pixels = normalize_roi_pixels(cv2.warpPerspective(probe.native, transform@probe.source, (768,768)))
            result = []
            for sigma in (0,2):
                p,d = local_features(cv2.GaussianBlur(pixels,(0,0),sigma) if sigma else pixels)
                result.append((probe.source, p/scale-unoffset, d))
            return result
        probe.views = [v for group in self._workers.map(extract, specs) for v in group]
        return probe.views

    def _legacy_probe(self, probe):
        if probe.legacy is None:
            shift = np.asarray([[1.,0,192],[0,1.,192],[0,0,1.]])
            context = cv2.warpPerspective(probe.native, shift@probe.source, (768,768))
            pixels = normalize_roi_pixels(cv2.warpPerspective(probe.native, probe.source, (384,384)))
            p,d = local_features(pixels)
            coarse = normalize_roi_pixels(context[192:576,192:576])
            secondary = local_features(cv2.GaussianBlur(coarse,(0,0),2.))
            primary = (probe.bank,context,probe.source,probe.native.shape[::-1],p,d)
            probe.legacy = primary,secondary
        return probe.legacy

    def score_gallery(self, probe, groups):
        pairs = {(user, j): min(self.base.match(p.astype(bool), sample[0])
                                for p in probe.bank if p[0,0] >= 0)
                 for user, samples in groups.items() for j, sample in enumerate(samples)}
        scores = {user:self._aggregate([pairs[(user,j)] for j in range(len(samples))])
                  for user,samples in groups.items()}
        ranking = sorted(scores.values())
        if len(ranking) >= 2 and ranking[0] <= .32 and ranking[1]-ranking[0] >= .08:
            probe.route = 'pose_confident'
            return scores
        probe.route = 'indexed_alignment'
        self.prepare_gallery(groups)
        with self._index_lock:
            if self._index is None: return scores
            primary,secondary = self._legacy_probe(probe)
            query_views = self._query_views(probe)
            votes = []
            for source,p,d in query_views:
                v = np.zeros(len(self._mapping))
                for matches in self._index.knnMatch(d, k=16) if len(d) else []:
                    seen = set()
                    for match in matches:
                        if match.distance > matches[0].distance*1.25+.02: continue
                        group = int(self._labels[match.trainIdx])
                        if group not in seen:
                            v[group] += 1/(match.distance+.1); seen.add(group)
                votes.append(v)
            def pair(key):
                user,j = key
                target_primary,target_secondary = groups[user][j][2]
                best = self.legacy._match_parts(primary,target_primary,[(secondary,target_secondary)])
                for (source,p,d),v in zip(query_views,votes):
                    selected = sorted(self._positions[key], key=lambda g:-v[g])[:3]
                    for group in selected:
                        if v[group] <= 0: continue
                        _,_,vi = self._mapping[group]
                        target = groups[user][j][1][vi]
                        transform = self.registration((p,d),(target[2],target[3]))
                        if transform is None: continue
                        warp = np.diag([1/3,1/3,1])@transform@source
                        corners = np.asarray([[0,0,1],[128,0,1],[128,128,1],[0,128,1]])@np.linalg.inv(warp).T
                        corners = corners[:,:2]/corners[:,2:]
                        if (not np.isfinite(corners).all() or (corners<1).any()
                            or (corners[:,0]>=probe.native.shape[1]-1).any()
                            or (corners[:,1]>=probe.native.shape[0]-1).any()
                            or not self._accept_alignment((None,None,probe.source),corners)): continue
                        pixels = normalize_roi_pixels(cv2.warpPerspective(probe.native,warp,(128,128)))
                        best = min(best, self.base.match(self.base.extract(pixels),target[4]))
                return key,best
            pairs.update(self._workers.map(pair, list(pairs)))
        return {user:self._aggregate([pairs[(user,j)] for j in range(len(samples))])
                for user,samples in groups.items()}

    def close(self):
        super().close()
        self._index = None
        self._references = None
