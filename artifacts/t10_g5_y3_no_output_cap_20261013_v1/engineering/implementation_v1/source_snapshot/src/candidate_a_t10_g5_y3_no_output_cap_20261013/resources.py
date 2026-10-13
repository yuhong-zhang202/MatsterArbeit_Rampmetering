"""Owned-child sampled watchdog independent of blocked TraCI calls."""
import shutil
import threading
import time


class ResourceWatchdog:
    def __init__(self, process, output, limits, started):
        self.process=process;self.output=output;self.limits=limits;self.started=started
        self.reason=None;self.error=None;self.done=threading.Event();self.thread=None
    def check_once(self):
        if self.process.poll() is not None:return
        try:
            if time.monotonic()-self.started>self.limits['wall_limit_s']:self.reason='WALL_LIMIT'
            elif shutil.disk_usage(self.output).free<self.limits['minimum_free_bytes']:self.reason='DISK_RESERVE'
            elif self.limits['run_limit_bytes'] is not None and sum(p.stat().st_size for p in self.output.rglob('*') if p.is_file())>self.limits['run_limit_bytes']:self.reason='OUTPUT_BYTES'
            if self.reason:
                self.process.terminate()
                try:self.process.wait(timeout=5)
                except Exception:self.process.kill();self.process.wait(timeout=5)
        except Exception as exc:
            self.error=type(exc).__name__+':'+str(exc);self.reason=self.reason or 'WATCHDOG_UNKNOWN'
            try:self.process.kill()
            except Exception:pass
    def _run(self):
        while not self.done.wait(.2):
            self.check_once()
            if self.reason or self.process.poll() is not None:return
    def start(self):
        self.thread=threading.Thread(target=self._run,name='owned-native-diagnostic-watchdog',daemon=True);self.thread.start()
    def close(self):
        self.done.set()
        if self.thread:self.thread.join(timeout=12)
        if self.thread and self.thread.is_alive():self.error='watchdog did not finish';self.reason=self.reason or 'WATCHDOG_UNKNOWN'
