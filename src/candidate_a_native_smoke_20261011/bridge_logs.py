"""Owned regular-file capture: no pipe reader race and no invented log silence."""
from pathlib import Path
import hashlib
import json
import os
import stat
import re


def require(ok, reason):
    if not ok:raise ValueError(reason)


class LogCapture:
    def __init__(self, output):
        self.output=Path(output)
        self.paths={n:self.output/n for n in ['sumo_stderr.log','sumo_stdout.log','sumo_error.log','sumo.log']}
        self.handles={}
        self.identity={}
        self.cursor={n:0 for n in self.paths}
        self.prefix={n:b'' for n in self.paths}
        self.records=[]
        for name,path in self.paths.items():
            handle=path.open('xb');self.handles[name]=handle
            info=os.fstat(handle.fileno());self.identity[name]=(info.st_dev,info.st_ino)
            require(stat.S_ISREG(info.st_mode),'not regular logfile')

    def snapshot(self, time_begin, time_end, stage):
        result={}
        for name,path in self.paths.items():
            require(path.is_file() and not path.is_symlink(),'missing/replaced logfile '+name)
            st=path.stat();require((st.st_dev,st.st_ino)==self.identity[name],'logfile inode replaced '+name)
            data=path.read_bytes();require(len(data)>=self.cursor[name] and data.startswith(self.prefix[name]),'logfile shrunk/rewritten '+name)
            require(path.stat().st_size==len(data),'concurrent/unbound log write '+name)
            fragment=data[self.cursor[name]:]
            # Decode the entire prefix: a multi-byte fragment never disappears.
            strict = name=='sumo_stderr.log' or stage=='AFTER_NATIVE_CLOSE_PROCESS_EOF'
            try:
                text=data.decode('utf-8','strict')
                decoded=True
            except UnicodeDecodeError:
                if strict:raise
                text=None;decoded=False
            if strict:require(not data or data.endswith(b'\n'),'partial native log line '+name)
            try:fragment_text=fragment.decode('utf-8','strict')
            except UnicodeDecodeError:fragment_text=None
            result[name]={'source':str(path),'byte_start':self.cursor[name],'byte_end':len(data),
                'device':st.st_dev,'inode':st.st_ino,'prefix_sha256':hashlib.sha256(data).hexdigest(),
                'fragment_sha256':hashlib.sha256(fragment).hexdigest(),'text':fragment_text,
                'raw_fragment_hex':fragment.hex(),'whole_prefix_decoded':decoded,
                'coverage':'CONDITIONAL_SYNC_CERR_BEFORE_ACK' if name=='sumo_stderr.log' else 'PROVISIONAL_UNTIL_PROCESS_EOF'}
            self.cursor[name]=len(data);self.prefix[name]=data
        record={'time_begin_s':time_begin,'time_end_s':time_end,'stage':stage,'streams':result}
        self.records.append(record)
        return record

    def adapter_warning(self, record):
        stderr=record['streams']['sumo_stderr.log']
        require(not stderr['text'],'native stderr nonempty: stop before another step')
        return {'time_begin_s':record['time_begin_s'],'time_end_s':record['time_end_s'],
            'coverage':'CALLER_DECLARED_INTERVAL','source':stderr['source'],
            'byte_start':stderr['byte_start'],'byte_end':stderr['byte_end'],'text':stderr['text'],
            'bridge_capture':stderr,'bridge_record_stage':record['stage'],
            'condition':'reviewed synchronous CERR path + stepACK; not universal/native safety proof'}

    def finalize(self, process, time_end, normal_closed):
        require(process.poll() is not None and process.returncode==0 and normal_closed,'normal process EOF not established')
        final=self.snapshot(time_end,time_end,'AFTER_NATIVE_CLOSE_PROCESS_EOF')
        late={n:r['byte_end']-r['byte_start'] for n,r in final['streams'].items()}
        # Buffered ordinary info is bound only to the whole final prefix, not
        # retroactively assigned a step. Critical late/no-source bytes fail.
        critical=late['sumo_stderr.log']>0 or bool(self.prefix['sumo_stderr.log']) or bool(self.prefix['sumo_error.log'])
        parsing_unverified=False
        reasons=['CRITICAL_STDERR_OR_ERROR_LOG_BYTES'] if critical else []
        for name in ['sumo_stdout.log','sumo.log']:
            info=self.prefix[name].decode('utf-8','strict').lower()
            for line in info.splitlines():
                # MSNet.cpp516-537 only emits positive event summaries. A
                # standalone zero-count synthetic line is not that native
                # format: retain UNKNOWN parsing, never call it an anomaly.
                zero=re.fullmatch(r'\s*(collisions|teleports): 0\s*',line)
                if zero:
                    parsing_unverified=True;reasons.append('LOG_PARSING_UNVERIFIED_ZERO_SUMMARY:'+name)
                elif any(token in line for token in ['warning:','error:','emergency braking','emergency stop','collision','teleport']):
                    critical=True;reasons.append('CRITICAL_OR_UNRECOGNIZED_EVENT_TEXT:'+name)
        status='UNKNOWN_OR_NATIVE_MESSAGE' if critical else ('UNKNOWN_LOG_PARSING_UNVERIFIED' if parsing_unverified else 'BOUND_NO_OBSERVED_NATIVE_MESSAGE')
        return {'coverage':'FINAL_FILES_AT_OWNED_PROCESS_EOF','process_returncode':process.returncode,
                'all_streams_bound':True,'late_bytes':late,'status':status,'reasons':reasons,
                'critical_message_observed_or_unrecognized':critical,'log_parsing_unverified':parsing_unverified,
                'per_step_complete_native_universal_claim':False,'record_count':len(self.records),
                'streams':final['streams']}

    def close_handles(self):
        for handle in self.handles.values():handle.close()
