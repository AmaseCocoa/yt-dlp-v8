import importlib.util
import secrets
import traceback

from STPyV8 import JSError
from yt_dlp.extractor.youtube.jsc._builtin.ejs import EJSBaseJCP
from yt_dlp.extractor.youtube.jsc.provider import (
    JsChallengeProvider,
    JsChallengeProviderError,
    JsChallengeRequest,
    JsChallengeType,
    register_preference,
    register_provider,
)

IS_AVALIABLE = True if importlib.util.find_spec("STPyV8") else False

if IS_AVALIABLE:
    import STPyV8
else:
    STPyV8 = None


@register_provider
class V8JsChallengeProviderJCP(
    EJSBaseJCP
):  # Provider class name must end with "JCP"
    PROVIDER_VERSION = "0.1.0"
    PROVIDER_NAME = "yt-dlp-v8"
    JS_RUNTIME_NAME = "v8"
    BUG_REPORT_LOCATION = "https://github.com/AmaseCocoa/yt-dlp-v8/issues"

    _SUPPORTED_TYPES = [JsChallengeType.N]

    def is_available(self) -> bool:
        return IS_AVALIABLE

    def _run_js_runtime(self, stdin: str, /) -> str:
        if not IS_AVALIABLE or not STPyV8:
            raise ValueError("STPyV8 Not found. this provider is unavaliable.")
        with STPyV8.JSIsolate():
            with STPyV8.JSContext() as ctxt:
                ctxt.securityToken = secrets.token_bytes(16)
                try:
                    result = ctxt.eval(stdin)
                except (
                    ReferenceError,
                    IndexError,
                    SyntaxError,
                    TypeError,
                    JSError,
                ) as e:
                    self.logger.trace(
                        f"Challange resolving error: {traceback.format_exc()}"
                    )
                    raise JsChallengeProviderError(repr(e), False)
                return str(result)


@register_preference(V8JsChallengeProviderJCP)
def v8_provider_preference(
    provider: JsChallengeProvider, requests: list[JsChallengeRequest]
) -> int:
    return 50
