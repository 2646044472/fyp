import unittest
from palm_app.frame_scheduler import Frame, LatestFrameScheduler


class SchedulerTests(unittest.TestCase):
    def test_latest_only_one_inflight_and_no_reuse(self):
        s = LatestFrameScheduler(); s.start()
        self.assertTrue(s.submit(Frame(1, 1., 'first')))
        first = s.claim(1.); self.assertEqual(first.frame.image, 'first')
        for i in range(2, 102): self.assertTrue(s.submit(Frame(i, 1., i)))
        self.assertIsNone(s.claim(1.))
        self.assertTrue(s.finish(first, now=1.))
        latest = s.claim(1.); self.assertEqual(latest.frame.frame_id, 101)
        self.assertTrue(s.finish(latest, now=1.))
        self.assertFalse(s.submit(Frame(101, 1., 'repeat')))
        self.assertIsNone(s.claim(1.))

    def test_cancel_suppresses_inflight_and_next_start_cannot_overlap(self):
        s = LatestFrameScheduler(); s.start(); s.submit(Frame(1, 1., None))
        old = s.claim(1.); s.cancel(); s.start(); s.submit(Frame(2, 2., None))
        self.assertIsNone(s.claim(2.))
        self.assertFalse(s.finish(old, now=2.))
        self.assertEqual(s.claim(2.).frame.frame_id, 2)

    def test_retry_and_expired_frame(self):
        s = LatestFrameScheduler(max_age_seconds=1.); s.start()
        s.submit(Frame(1, 1., None)); one = s.claim(1.)
        s.finish(one, now=1., retry_after=.5)
        s.submit(Frame(2, 1.1, None)); self.assertIsNone(s.claim(1.49))
        self.assertIsNone(s.claim(2.2))
        s.submit(Frame(3, 2.2, None)); self.assertEqual(s.claim(2.2).frame.frame_id, 3)

    def test_cancel_drops_pending(self):
        s = LatestFrameScheduler(); s.start(); s.submit(Frame(1, 1., None)); s.cancel()
        self.assertFalse(s.submit(Frame(2, 1., None))); s.start()
        self.assertIsNone(s.claim(1.))
        self.assertFalse(s.submit(Frame(1, 1., None)))


if __name__ == '__main__': unittest.main()
