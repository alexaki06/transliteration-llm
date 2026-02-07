import asyncio
import shutil
from typing import AsyncIterator


class OllamaStreamingClient:
    """Streams output from the `ollama run <model>` CLI using an async subprocess.

    Notes:
    - Requires the `ollama` executable on PATH. If not available, instantiation raises RuntimeError.
    - The implementation writes the prompt to the process stdin and reads stdout in binary chunks,
      decoding and yielding text as it arrives.
    """

    def __init__(self, model: str = "mistral"):
        self.model = model
        self.cmd = shutil.which("ollama")
        if not self.cmd:
            raise RuntimeError("'ollama' executable not found on PATH")

    async def stream_generate(self, prompt: str) -> AsyncIterator[str]:
        proc = await asyncio.create_subprocess_exec(
            self.cmd, "run", self.model,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Send prompt and close stdin to signal end of input
        try:
            proc.stdin.write(prompt.encode())
            await proc.stdin.drain()
            proc.stdin.close()
        except Exception:
            # If writing to stdin fails, terminate
            proc.kill()
            await proc.wait()
            raise

        # Read stdout incrementally
        while True:
            chunk = await proc.stdout.read(1024)
            if not chunk:
                break
            try:
                text = chunk.decode()
            except UnicodeDecodeError:
                text = chunk.decode(errors="ignore")
            yield text

        # Wait for process completion and check for non-zero exit
        await proc.wait()
        if proc.returncode != 0:
            err = await proc.stderr.read()
            try:
                err_text = err.decode()
            except Exception:
                err_text = str(err)
            raise RuntimeError(f"Ollama returned non-zero exit: {err_text}")
