from .provider import Challenge, Result

class MockAuthorizationProvider:
    def authorize(self, challenge: Challenge, identity: str) -> Result:
        return Result(challenge, identity)

