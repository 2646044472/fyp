"""Isolated same-model ONNX resource sharing; never imported by production."""
from pklnet_roi import PKLNetROI


def shared_heatmap_view(source):
    """Separate heatmap policy, same validated ONNX graph/session and run lock.

    No inference result, tensor, ROI, descriptor or identity answer is cached.
    Every extract still performs its original ONNX run and postprocessing.
    """
    if source.policy=='legacy':
        raise ValueError('Legacy graph is not the diagnostic branch graph')
    source._ensure_loaded()
    if source._session is None or source._model is not None or source.backend_used!='onnx':
        raise ValueError('This isolated pilot requires the loaded ONNX backend')
    child=PKLNetROI(root=source.root,weights=source.weights,backend=source.backend,
                    threads=source.threads,policy='heatmap')
    assert child.root.resolve()==source.root.resolve() and child.weights.resolve()==source.weights.resolve()
    child._session=source._session
    child._roi_extractor=source._roi_extractor
    child._inference_lock=source._inference_lock
    child.backend_used=source.backend_used
    return child
