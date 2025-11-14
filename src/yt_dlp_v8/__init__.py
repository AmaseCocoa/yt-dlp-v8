import importlib.util
import json
import subprocess
import typing

from yt_dlp.extractor.youtube.jsc.provider import (
    JsChallengeProvider,
    JsChallengeProviderError,
    JsChallengeProviderRejectedRequest,
    JsChallengeProviderResponse,
    JsChallengeRequest,
    JsChallengeResponse,
    JsChallengeType,
    NChallengeOutput,
    register_preference,
    register_provider,
)
from yt_dlp.utils import Popen, classproperty, traverse_obj


@register_provider
class V8JsChallengeProviderJCP(
    JsChallengeProvider
):  # Provider class name must end with "JCP"
    PROVIDER_VERSION = "0.1.0"
    PROVIDER_NAME = "yt-dlp-v8"
    BUG_REPORT_LOCATION = "https://github.com/AmaseCocoa/yt-dlp-v8/issues"

    _SUPPORTED_TYPES = [JsChallengeType.N]

    def is_available(self) -> bool:
        return True if importlib.util.find_spec("STPyV8") else False

    def close(self):
        # Optional close hook, called when YoutubeDL is closed.
        pass

    def _real_bulk_solve(
        self, requests: list[JsChallengeRequest]
    ) -> typing.Generator[JsChallengeProviderResponse, None, None]:
        # ℹ️ If you need to do additional validation on the requests.
        # Raise yt_dlp.extractor.youtube.jsc.provider.JsChallengeProviderRejectedRequest if the request is not supported.
        if len("something") > 255:
            raise JsChallengeProviderRejectedRequest(
                "Challenges longer than 255 are not supported", expected=True
            )

        # ℹ️ Settings are pulled from extractor args passed to yt-dlp with the key `youtubejsc-<PROVIDER_KEY>`.
        # For this example, the extractor arg would be:
        # `--extractor-args "youtubejsc-myjschallengeprovider:bin_path=/path/to/bin"`
        bin_path = self._configuration_arg(
            "bin_path", default=["/path/to/bin"]
        )[0]

        # See below for logging guidelines
        self.logger.trace(f"Using bin path: {bin_path}")

        for request in requests:
            # You can use the _get_player method to get the player JS code if needed.
            # This shares the same caching as the YouTube extractor, so it will not make unnecessary requests.
            player_js = self._get_player(
                request.video_id, request.input.player_url
            )
            cmd = f"{bin_path} {request.input.challenges} {player_js}"
            self.logger.info(f"Executing command: {cmd}")
            stdout, _, ret = Popen.run(
                cmd, text=True, shell=True, stdout=subprocess.PIPE
            )
            if ret != 0:
                # ℹ️ If there is an error, raise JsChallengeProviderError.
                # The request will be sent to the next provider if there is one.
                # You can specify whether it is expected or not. If it is unexpected,
                #  the log will include a link to the bug report location (BUG_REPORT_LOCATION).

                # raise JsChallengeProviderError(f'Command returned error code {ret}', expected=False)

                # You can also only fail this specific request by returning a JsChallengeProviderResponse with the error.
                # This will allow other requests to be processed by this provider.
                yield JsChallengeProviderResponse(
                    request=request,
                    error=JsChallengeProviderError(
                        f"Command returned error code {ret}", expected=False
                    ),
                )

            yield JsChallengeProviderResponse(
                request=request,
                response=JsChallengeResponse(
                    type=JsChallengeType.N,
                    output=NChallengeOutput(
                        results=traverse_obj(json.loads(stdout))
                    ),
                ),
            )


# If there are multiple JS Challenge Providers that can handle the same JsChallengeRequest(s),
# you can define a preference function to increase/decrease the priority of providers.


@register_preference(MyJsChallengeProviderJCP)
def my_provider_preference(
    provider: JsChallengeProvider, requests: list[JsChallengeRequest]
) -> int:
    return 50
