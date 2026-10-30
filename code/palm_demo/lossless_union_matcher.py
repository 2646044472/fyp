"""Explicit v27 container experiment; v26 scoring/extraction code is inherited."""
from compnet_alternate_roi_matcher import CompNetAlternateROIMatcher
from union_lossless_codec import CODEC,decode,pack


class LosslessUnionMatcher(CompNetAlternateROIMatcher):
    name='FastCCCompNetAlternateROI-v27-lossless-experimental'
    magic=2801166
    template_codec=CODEC
    template_storage_schema='union-five-frame-npz-v2'

    @staticmethod
    def template_store_factory(root,**kwargs):
        from lossless_template_store import LosslessTemplateStore
        return LosslessTemplateStore(root,**kwargs)

    def _pack(self,legacy,png,queries,gallery):
        return pack(legacy,png,queries,gallery)

    def _unpack(self,feature,*,decode_native=True):
        return decode(feature,decode_native=decode_native).parts

    def upgrade_v4_template(self,feature):
        raise ValueError('v4 migration is not certified for the v27 container experiment')
