"""Pristine-only recovery for the interrupted M9 v3 source_build transaction."""
import base64
import fcntl
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import time

PROJECT = Path('/mnt/e/Projects/Codex/DeepH')
ROOT = Path('/home/evan-williams/deeph-m9')
AUDITS = PROJECT / '08_audits'
SELF = PROJECT / '06_reproduction/controllers/m9_source_build_host_shutdown_recovery_v1.py'
TEST = PROJECT / '06_reproduction/tests/test_m9_source_build_host_shutdown_recovery_v1.py'
WORK = AUDITS / 'M9_source_build_host_shutdown_recovery_v1_work_package.md'
AUTH = PROJECT / '00_scope/D019_standing_execution_authorization.md'
INTERRUPTION_REPORT = AUDITS / 'M9_source_build_v3_interruption_independent_audit.md'
INTERRUPTION_EVIDENCE = AUDITS / 'M9_source_build_v3_interruption_postexecution_evidence.json'
PREEXECUTION_EVIDENCE = AUDITS / 'M9_source_build_v3_preexecution_evidence.json'
RECEIPTS = PROJECT / '06_reproduction/controllers/m9_py39_consumer_gate_completion.py'
BUDGET = PROJECT / '06_reproduction/scripts/m9_budget.py'
V3_MANIFEST = PROJECT / '06_reproduction/manifests/m9_source_build_v3_frozen_hashes.json'
FROZEN = PROJECT / '06_reproduction/manifests/m9_source_build_host_shutdown_recovery_v1_frozen_hashes.json'
REPORT = AUDITS / 'M9_source_build_host_shutdown_recovery_v1_implementation_audit.md'
VERDICT = AUDITS / 'M9_source_build_host_shutdown_recovery_v1_implementation_verdict.json'

LOCK = ROOT / 'manifests/budget.lock'
STATE = ROOT / 'manifests/budget_state.json'
WORKFLOW = ROOT / 'manifests/overlap_workflow_state.json'
TX = ROOT / 'manifests/overlap_transaction.json'
LEDGER = ROOT / 'manifests/budget_ledger.jsonl'
CAPABILITY = ROOT / 'manifests/overlap_capabilities/3cd45d83e11ec6fe0e39725dfe7c6d79.consumed.json'
RECEIPT = ROOT / 'manifests/overlap_capabilities/3cd45d83e11ec6fe0e39725dfe7c6d79.launcher-receipt.json'
PERMIT = ROOT / 'manifests/source_build_v3_execution_permit.json'
BUILD = ROOT / 'software/openmx-overlap-build'
CLEAN = ROOT / 'software/openmx-overlap-build.failed-80e28da82f076f4f7b1811f5897216bd.retired'
LOGS = ROOT / 'logs/overlap-build'
RECOVERY_ID = 'm9-source-build-host-shutdown-recovery-20260901-01'
FAILURE_ID = '4d7808af7df9418518a59afeba766eb9'
CAPABILITY_ID = '3cd45d83e11ec6fe0e39725dfe7c6d79'
ARCHIVE = BUILD.with_name('openmx-overlap-build.interrupted-' + FAILURE_ID + '.retired')
LOG_ARCHIVE = LOGS.with_name('overlap-build.interrupted-' + FAILURE_ID + '.retired')
STAGING = BUILD.with_name(BUILD.name + '.host-shutdown-recovery.staging')
PRIVATE = Path('/root/deeph-m9-control/source-build-host-shutdown-recovery-v1')
SNAPSHOT = ROOT / 'controls/source-build-host-shutdown-recovery-v1'
JOURNAL = PRIVATE / 'journal.json'
SHUTDOWN_UTC = '2026-08-31T15:24:41.9861032Z'
ELAPSED = 292.7759032
RECOVERY_FORECAST = 1073741824
INTERRUPTION_REPORT_SHA = '410468cea26e8d7359f400d3a3e1dbeb7723e2120560c89a2f093c0009d07104'
INTERRUPTION_EVIDENCE_SHA = '12907e82278f114e228c0b9e930564dafd18ab761159f70edd01ac2200f2f3d2'
PREEXECUTION_EVIDENCE_SHA = '822e0fc61599db3b1b1135b2e384050ca373f0c4c08aea84bee70d7a3cee3b43'
RECEIPTS_SHA = 'c2c235c444bae0f613078a060efa9733f869533385fa84268bfd2cc2b3c3ef55'
V3_MANIFEST_SHA = '01a2a8f438d27d582abcf4536775b54605051a3458b06f2bc29c2c56222d4e58'
AUTH_SHA = '4f44e839d2deccf8a4fd172ad9a45243ad446c1009d1f09666f26f2c23ba28e0'
EXPECTED_INTERRUPTED_TREE = 'afbeae908757c7e4f26010f39543a54503210fff9d24c71845bba9cf688dfed3'
EXPECTED_CLEAN_TREE = '060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359'
SOURCE_SET = {SELF, TEST, WORK, AUTH, INTERRUPTION_REPORT, INTERRUPTION_EVIDENCE,
              PREEXECUTION_EVIDENCE, RECEIPTS, V3_MANIFEST}
PHASES = ('PREPARED', 'INTERRUPTED_ARCHIVED', 'LOGS_ARCHIVED', 'CLEAN_TREE_CLONED',
          'LEDGER_COMMITTED', 'TRANSACTION_COMMITTED', 'STATE_COMMITTED',
          'WORKFLOW_COMMITTED', 'SUCCESS_COMMITTED')
ACTIVE_LOCK_FD = None
ACTIVE_LOCK_IDENTITY = None


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')


def canonical(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode('utf-8'))


def pinned(path, expected=None):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        a = os.fstat(fd)
        chunks = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        raw = b''.join(chunks)
        b, linked = os.fstat(fd), os.lstat(path)
        fields = ('st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink',
                  'st_size','st_mtime_ns','st_ctime_ns')
        if (not stat.S_ISREG(a.st_mode) or a.st_nlink != 1 or len(raw) != a.st_size
                or any(getattr(a,k) != getattr(b,k) or getattr(b,k) != getattr(linked,k)
                       for k in fields)
                or expected is not None and sha(raw) != expected):
            raise ValueError('pinned recovery source differs: ' + str(path))
        return raw
    finally:
        os.close(fd)


def load_source(name, path, raw):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def authority(argv):
    if len(argv) != 5 or argv[1] not in ('preflight', 'recover'):
        raise ValueError('expected self_sha preflight|recover frozen_sha verdict_sha report_sha; no resume')
    self_sha, action, frozen_sha, verdict_sha, report_sha = argv
    payloads = {FROZEN:pinned(FROZEN,frozen_sha), REPORT:pinned(REPORT,report_sha),
                VERDICT:pinned(VERDICT,verdict_sha)}
    frozen = json.loads(payloads[FROZEN])
    if (set(frozen) != {'schema','files'}
            or frozen['schema'] != 'm9-host-shutdown-recovery-frozen-v1'
            or set(frozen['files']) != {str(p) for p in SOURCE_SET}):
        raise ValueError('host-shutdown recovery source closure differs')
    for name, digest in frozen['files'].items():
        payloads[Path(name)] = pinned(Path(name), digest)
    if (frozen['files'][str(SELF)] != self_sha
            or sha(payloads[INTERRUPTION_REPORT]) != INTERRUPTION_REPORT_SHA
            or sha(payloads[INTERRUPTION_EVIDENCE]) != INTERRUPTION_EVIDENCE_SHA
            or sha(payloads[PREEXECUTION_EVIDENCE]) != PREEXECUTION_EVIDENCE_SHA
            or sha(payloads[RECEIPTS]) != RECEIPTS_SHA
            or sha(payloads[V3_MANIFEST]) != V3_MANIFEST_SHA
            or sha(payloads[AUTH]) != AUTH_SHA):
        raise ValueError('host-shutdown recovery historical binding differs')
    verdict = json.loads(payloads[VERDICT])
    expected = {'schema':'m9-host-shutdown-recovery-implementation-verdict-v1',
        'status':'PASS','blocking':0,'non_blocking':0,'frozen_sha256':frozen_sha,
        'report_path':str(REPORT),'report_sha256':report_sha}
    if verdict != expected or type(verdict['blocking']) is not int or type(verdict['non_blocking']) is not int:
        raise ValueError('host-shutdown recovery independent authority differs')
    # Revalidate every v3 nested source without importing or executing it.
    v3 = json.loads(payloads[V3_MANIFEST])
    if v3.get('schema') != 'm9-source-build-frozen-v3':
        raise ValueError('v3 frozen schema differs')
    nested_digests = {}
    for name, digest in v3['files'].items():
        nested_raw = pinned(Path(name), digest)
        try:
            nested = json.loads(nested_raw)
        except (UnicodeDecodeError, json.JSONDecodeError):
            nested = None
        if isinstance(nested, dict) and isinstance(nested.get('files'), dict):
            for member, member_sha in nested['files'].items():
                old = nested_digests.setdefault(member, member_sha)
                if old != member_sha:
                    raise ValueError('nested frozen source digest conflict: ' + member)
    for name, digest in nested_digests.items():
        pinned(Path(name), digest)
    if str(BUDGET) not in nested_digests:
        raise ValueError('nested frozen closure lacks original budget')
    reader = load_source('m9_host_shutdown_receipts', RECEIPTS, payloads[RECEIPTS])
    budget = load_source('m9_host_shutdown_budget_readonly', BUDGET,
                         pinned(BUDGET, nested_digests[str(BUDGET)]))
    return action, payloads, reader, budget


def formal_namespace(reader):
    result = {}
    for root in (ROOT / 'manifests', ROOT / 'controls', Path('/root/deeph-m9-control')):
        result.update(reader.capture_tree(root))
    return result


def decoded_formal(evidence):
    if evidence['formal_namespace_encoding'] != 'canonical-json-gzip-base64':
        raise ValueError('interruption namespace encoding differs')
    raw = gzip.decompress(base64.b64decode(evidence['formal_namespace_json_gzip_base64'], validate=True))
    if len(raw) != evidence['formal_namespace_json_bytes'] or sha(raw) != evidence['formal_namespace_sha256']:
        raise ValueError('interruption namespace payload differs')
    value = json.loads(raw)
    if canonical(value) != evidence['formal_namespace_sha256'] or len(value) != 221:
        raise ValueError('interruption namespace identity differs')
    return value


def portable_tree(root, reader):
    full = reader.capture_tree(root)
    return portable_receipts(full, root)


def portable_receipts(full, root):
    result = {}
    prefix = str(root)
    for name, item in full.items():
        relative = '.' if name == prefix else name[len(prefix)+1:]
        value = {k:v for k,v in item.items()
                 if k not in {'path','dev','ino','mtime_ns','ctime_ns','bytes'}}
        if item['kind'] == 'file':
            value['bytes'] = item['bytes']
        result[relative] = value
    return result


def process_alive(capability):
    expected = []
    for field in ('budget_argv','launcher_argv'):
        expected.append(b'\0'.join(str(x).encode() for x in capability[field]) + b'\0')
    for entry in Path('/proc').iterdir():
        if not entry.name.isdecimal():
            continue
        try:
            raw = (entry / 'cmdline').read_bytes()
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
        if raw in expected:
            return True
    return False


def raw_runtime(evidence):
    result = {}
    for name, value in evidence['runtime_raw_bytes'].items():
        raw = base64.b64decode(value['base64'], validate=True)
        if len(raw) != value['bytes'] or sha(raw) != value['sha256']:
            raise ValueError('interruption runtime evidence differs')
        result[Path(name)] = raw
    if set(result) != {STATE, WORKFLOW, TX, LEDGER}:
        raise ValueError('interruption runtime closure differs')
    return result


def targets(raw, payloads):
    state, workflow, tx = (json.loads(raw[p]) for p in (STATE,WORKFLOW,TX))
    if (state.get('active_overlap_transaction') != FAILURE_ID or state.get('hard_stopped')
            or workflow.get('active_transaction') != FAILURE_ID or workflow.get('hard_stopped')
            or workflow.get('stage') != 'SOURCES_PREPARED'
            or tx.get('transaction_id') != FAILURE_ID or tx.get('state') != 'RUNNING'
            or tx.get('action') != 'source_build' or tx.get('child_pid') != 396
            or tx.get('start_utc') != '2026-08-31T15:19:49.210200Z'):
        raise ValueError('orphaned transaction semantics differ')
    old_cpu = float(state['cpu_seconds']['overlap_build'])
    if old_cpu != 7214.469142588001:
        raise ValueError('orphaned transaction accounting parent differs')
    state['cpu_seconds']['overlap_build'] = old_cpu + ELAPSED
    state['active_overlap_transaction'] = None
    state['last_event_utc'] = SHUTDOWN_UTC
    state['recovered_from_source_build_host_shutdown'] = RECOVERY_ID
    workflow['active_transaction'] = None
    workflow['hard_stopped'] = False
    workflow['stage'] = 'SOURCES_PREPARED'
    workflow['recovered_from_source_build_host_shutdown'] = RECOVERY_ID
    tx.update({'state':'FAILED_COMMITTED','end_utc':SHUTDOWN_UTC,
        'elapsed_seconds':ELAPSED,'elapsed_semantics':'conservative_wall_upper_bound_not_measured_cpu',
        'exit_code':None,'timed_out':False,'reasons':['host_shutdown_external_interruption'],
        'launcher_receipt_sha256':None,'recovery_id':RECOVERY_ID,
        'interruption_report_sha256':INTERRUPTION_REPORT_SHA,
        'interruption_evidence_sha256':INTERRUPTION_EVIDENCE_SHA})
    event = {'event':'SOURCE_BUILD_HOST_SHUTDOWN_RECOVERY','event_id':RECOVERY_ID,
        'utc':SHUTDOWN_UTC,'parent_transaction_id':FAILURE_ID,
        'parent_transaction_sha256':sha(raw[TX]),'ledger_prefix_sha256':sha(raw[LEDGER]),
        'ledger_prefix_bytes':len(raw[LEDGER]),'elapsed_seconds':ELAPSED,
        'elapsed_semantics':'conservative_wall_upper_bound_not_measured_cpu',
        'cpu_seconds':state['cpu_seconds'],'gpu_seconds':state['gpu_seconds'],
        'cpu_adjustments':state['cpu_adjustments'],'source_build_authorized':False,
        'authorization':{'d019_sha256':sha(payloads[AUTH]),
            'interruption_report_sha256':sha(payloads[INTERRUPTION_REPORT]),
            'interruption_evidence_sha256':sha(payloads[INTERRUPTION_EVIDENCE]),
            'frozen_sha256':sha(payloads[FROZEN]),'implementation_report_sha256':sha(payloads[REPORT]),
            'implementation_verdict_sha256':sha(payloads[VERDICT])}}
    line = (json.dumps(event,ensure_ascii=False,sort_keys=True)+'\n').encode('utf-8')
    return {STATE:encode(state),WORKFLOW:encode(workflow),TX:encode(tx),LEDGER:raw[LEDGER]+line},event,line


def require_pristine():
    forbidden = (ARCHIVE,LOG_ARCHIVE,STAGING,PRIVATE,SNAPSHOT,
        STATE.with_name(STATE.name+'.host-shutdown-recovery.tmp'),
        WORKFLOW.with_name(WORKFLOW.name+'.host-shutdown-recovery.tmp'),
        TX.with_name(TX.name+'.host-shutdown-recovery.tmp'))
    for path in forbidden:
        if os.path.lexists(path):
            raise ValueError('non-pristine recovery target; preserve and stop: '+str(path))


def sync_dir(path):
    fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try: os.fsync(fd)
    finally: os.close(fd)


def assert_lock():
    if ACTIVE_LOCK_FD is None:
        return
    descriptor, linked = os.fstat(ACTIVE_LOCK_FD), os.lstat(LOCK)
    fields=('st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink','st_size')
    current=tuple(getattr(descriptor,k) for k in fields)
    if (current != ACTIVE_LOCK_IDENTITY
            or tuple(getattr(linked,k) for k in fields) != ACTIVE_LOCK_IDENTITY):
        raise ValueError('budget lock identity drift')


def write_file(path,raw,uid=0,gid=0,mode=0o600,replace=False):
    temporary = path.with_name(path.name+'.host-shutdown-recovery.tmp') if replace else path
    if os.path.lexists(temporary):
        raise FileExistsError(str(temporary))
    fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,mode)
    try:
        os.fchown(fd,uid,gid); os.fchmod(fd,mode)
        offset=0
        while offset<len(raw):
            count=os.write(fd,raw[offset:])
            if count<=0: raise OSError('short recovery write')
            offset+=count
        os.fsync(fd)
    finally: os.close(fd)
    if replace: os.replace(temporary,path)
    if pinned(path,sha(raw)) != raw: raise ValueError('recovery written bytes differ')
    sync_dir(path.parent)


def checkpoint(journal,phase):
    assert_lock()
    if phase != PHASES[len(journal['history'])]:
        raise ValueError('recovery phase order differs')
    journal['phase']=phase
    journal['history'].append({'phase':phase,'runtime':{
        str(p):sha(pinned(p,None)) for p in (STATE,WORKFLOW,TX,LEDGER)}})
    write_file(JOURNAL,encode(journal),replace=os.path.lexists(JOURNAL))
    assert_lock()


def copy_owned(source,destination):
    shutil.copyfile(source,destination,follow_symlinks=False)
    shutil.copystat(source,destination,follow_symlinks=False)
    meta=os.stat(source,follow_symlinks=False)
    os.chown(destination,meta.st_uid,meta.st_gid,follow_symlinks=False)
    fd=os.open(destination,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        copied=os.fstat(fd)
        if not stat.S_ISREG(copied.st_mode) or copied.st_nlink != 1:
            raise ValueError('recovery clone member is not an independent regular file')
        os.fsync(fd)
    finally:
        os.close(fd)
    return destination


def verify_no_hardlinks(source,destination):
    source_files={p.relative_to(source):os.lstat(p) for p in source.rglob('*')
                  if stat.S_ISREG(os.lstat(p).st_mode)}
    destination_files={p.relative_to(destination):os.lstat(p) for p in destination.rglob('*')
                       if stat.S_ISREG(os.lstat(p).st_mode)}
    if set(source_files)!=set(destination_files):
        raise ValueError('recovery clone regular-file closure differs')
    for relative,src in source_files.items():
        dst=destination_files[relative]
        if dst.st_nlink != 1 or (src.st_dev,src.st_ino)==(dst.st_dev,dst.st_ino):
            raise ValueError('recovery clone contains a hard link')


def clone_tree(source,destination):
    shutil.copytree(source,destination,symlinks=True,copy_function=copy_owned)
    for src in sorted((p for p in source.rglob('*') if p.is_dir() and not p.is_symlink()),
                      key=lambda p:len(p.parts),reverse=True):
        dst=destination/src.relative_to(source)
        meta=src.stat(); os.chown(dst,meta.st_uid,meta.st_gid); shutil.copystat(src,dst)
    meta=source.stat(); os.chown(destination,meta.st_uid,meta.st_gid); shutil.copystat(source,destination)
    verify_no_hardlinks(source,destination)
    directories=[destination,*[p for p in destination.rglob('*')
                                if p.is_dir() and not p.is_symlink()]]
    for path in sorted(directories,key=lambda p:len(p.parts),reverse=True):
        sync_dir(path)
    sync_dir(destination.parent)


def append_ledger(prefix,line):
    before=os.lstat(LEDGER)
    fd=os.open(LEDGER,os.O_RDWR|os.O_APPEND|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        if os.pread(fd,len(prefix)+1,0)!=prefix: raise ValueError('ledger prefix differs')
        offset=0
        while offset<len(line):
            count=os.write(fd,line[offset:])
            if count<=0: raise OSError('short ledger write')
            offset+=count
        os.fsync(fd)
    finally: os.close(fd)
    after=os.lstat(LEDGER)
    fields=('st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink')
    if (pinned(LEDGER,sha(prefix+line)) != prefix+line
            or any(getattr(before,k)!=getattr(after,k) for k in fields)):
        raise ValueError('ledger append differs')


def verify_current(payloads,reader,budget,evidence,expected,raw):
    assert_lock()
    require_pristine()
    for path,data in payloads.items():
        pinned(path,sha(data))
    current_formal=formal_namespace(reader)
    if current_formal!=expected:
        raise ValueError('formal interruption namespace drift')
    for path,data in raw.items():
        if pinned(path,sha(data))!=data: raise ValueError('formal runtime raw bytes drift')
    capability_raw=pinned(CAPABILITY,None)
    capability=json.loads(capability_raw)
    process_present=process_alive(capability)
    if (capability!=evidence['consumed_capability'] or capability.get('state')!='CONSUMED'
            or capability.get('capability_id')!=CAPABILITY_ID or os.path.lexists(RECEIPT)
            or process_present):
        raise ValueError('consumed capability or orphan process semantics differ')
    permit_raw=pinned(PERMIT,None)
    if sha(permit_raw)!=evidence['permit_receipt']['sha256']:
        raise ValueError('v3 permit drift')
    interrupted_receipts=reader.capture_tree(BUILD)
    clean_receipts=reader.capture_tree(CLEAN)
    if canonical(interrupted_receipts)!=EXPECTED_INTERRUPTED_TREE:
        raise ValueError('interrupted build tree drift')
    if canonical(clean_receipts)!=EXPECTED_CLEAN_TREE:
        raise ValueError('clean historical tree drift')
    interrupted_portable=portable_receipts(interrupted_receipts,BUILD)
    clean_portable=portable_receipts(clean_receipts,CLEAN)
    if clean_portable==interrupted_portable:
        raise ValueError('interrupted tree unexpectedly pristine')
    log_paths={str(LOGS),*(str(p) for p in LOGS.iterdir())}
    if set(evidence['logs'])!=log_paths:
        raise ValueError('interrupted log path closure differs')
    log_evidence={}
    for name,wanted in evidence['logs'].items():
        actual=reader.filesystem_receipt(Path(name))
        if actual!=wanted: raise ValueError('interrupted log drift')
        log_evidence[name]=actual
    log_receipts=reader.capture_tree(LOGS)
    products={}
    for name,present in evidence['products_present'].items():
        products[name]=os.path.lexists(name)
        if present or products[name]: raise ValueError('forbidden interrupted product appeared')
    issues=budget.violations(json.loads(raw[STATE]),RECOVERY_FORECAST)
    if issues:
        raise ValueError('host-shutdown recovery storage forecast rejected: '+repr(issues))
    storage=(budget.storage_snapshot(json.loads(raw[STATE]))
             if hasattr(budget,'storage_snapshot') else None)
    assert_lock()
    return {'formal':current_formal,'raw_sha256':{str(p):sha(v) for p,v in raw.items()},
        'capability_sha256':sha(capability_raw),'capability':capability,
        'process_present':process_present,'receipt_present':os.path.lexists(RECEIPT),
        'permit_sha256':sha(permit_raw),'interrupted_receipts':interrupted_receipts,
        'interrupted_portable':interrupted_portable,'clean_receipts':clean_receipts,
        'clean_portable':clean_portable,'log_paths':sorted(log_paths),
        'log_evidence':log_evidence,'log_receipts':log_receipts,'products_present':products,
        'budget_violations':list(issues),'storage_snapshot':storage}


def validate(action,payloads,reader,budget):
    assert_lock()
    evidence=json.loads(payloads[INTERRUPTION_EVIDENCE])
    if (evidence.get('status')!='INTERRUPTED_NONTERMINAL' or evidence.get('blocking')!=1
            or evidence.get('non_blocking')!=0 or evidence.get('formal_count')!=221
            or evidence.get('conservative_elapsed_upper_bound_seconds')!=ELAPSED):
        raise ValueError('interruption evidence verdict differs')
    expected=decoded_formal(evidence)
    raw=raw_runtime(evidence)
    target,event,line=targets(raw,payloads)
    seal=verify_current(payloads,reader,budget,evidence,expected,raw)
    if action=='preflight':
        second=verify_current(payloads,reader,budget,evidence,expected,raw)
        if second!=seal: raise ValueError('preflight object set changed')
        assert_lock()
        return {'status':'PREFLIGHT_PASS','writes':0,'source_build_authorized':False,
                'elapsed_upper_bound_seconds':ELAPSED,'forecast_bytes':RECOVERY_FORECAST}
    return commit(payloads,reader,budget,evidence,expected,raw,target,event,line,seal)


def commit(payloads,reader,budget,evidence,expected,raw,target,event,line,seal):
    started=time.monotonic()
    # Recheck every sealed authority and mutable input immediately before mutation.
    try:
        current=verify_current(payloads,reader,budget,evidence,expected,raw)
    except Exception as error:
        raise ValueError('recovery object drift before first write: '+str(error)) from error
    if current!=seal:
        raise ValueError('recovery object drift before first write')
    clean_portable=seal['clean_portable']
    interrupted_receipts=seal['interrupted_receipts']
    log_receipts=seal['log_receipts']
    os.mkdir(PRIVATE,0o700); os.chown(PRIVATE,0,0); os.chmod(PRIVATE,0o700); sync_dir(PRIVATE.parent)
    for path,data in sorted(payloads.items(),key=lambda item:str(item[0])):
        write_file(PRIVATE/path.name,data)
    for path,data in raw.items(): write_file(PRIVATE/('before-'+path.name),data)
    journal={'schema':'m9-source-build-host-shutdown-recovery-journal-v1',
        'recovery_id':RECOVERY_ID,'parent_transaction_id':FAILURE_ID,'history':[],
        'interruption_tree_sha256':EXPECTED_INTERRUPTED_TREE,'clean_tree_sha256':EXPECTED_CLEAN_TREE,
        'event':event,'event_line_base64':base64.b64encode(line).decode('ascii'),
        'target_sha256':{str(p):sha(v) for p,v in target.items()},'source_build_authorized':False}
    checkpoint(journal,'PREPARED')
    os.rename(BUILD,ARCHIVE); sync_dir(BUILD.parent)
    archived=reader.capture_tree(ARCHIVE)
    if len(archived)!=len(interrupted_receipts): raise ValueError('interrupted archive count differs')
    for old,item in interrupted_receipts.items():
        rel=Path(old).relative_to(BUILD); moved=archived[str(ARCHIVE/rel) if str(rel)!='.' else str(ARCHIVE)]
        for key in ('dev','ino','uid','gid','mode','nlink','bytes','kind','sha256'):
            if key in item and moved.get(key)!=item[key]: raise ValueError('interrupted archive identity differs')
    checkpoint(journal,'INTERRUPTED_ARCHIVED')
    os.rename(LOGS,LOG_ARCHIVE); sync_dir(LOGS.parent)
    moved_logs=reader.capture_tree(LOG_ARCHIVE)
    if len(moved_logs)!=len(log_receipts): raise ValueError('interrupted log archive count differs')
    for old,item in log_receipts.items():
        rel=Path(old).relative_to(LOGS); key=str(LOG_ARCHIVE/rel) if str(rel)!='.' else str(LOG_ARCHIVE)
        moved=moved_logs[key]
        for field in ('dev','ino','uid','gid','mode','nlink','bytes','kind','sha256'):
            if field in item and moved.get(field)!=item[field]: raise ValueError('interrupted log archive identity differs')
    checkpoint(journal,'LOGS_ARCHIVED')
    clone_tree(CLEAN,STAGING)
    if portable_tree(STAGING,reader)!=clean_portable: raise ValueError('clean clone differs')
    verify_no_hardlinks(CLEAN,STAGING)
    os.rename(STAGING,BUILD); sync_dir(BUILD.parent)
    if portable_tree(BUILD,reader)!=clean_portable or canonical(reader.capture_tree(CLEAN))!=EXPECTED_CLEAN_TREE:
        raise ValueError('installed clean tree or historical source differs')
    checkpoint(journal,'CLEAN_TREE_CLONED')
    append_ledger(raw[LEDGER],line); checkpoint(journal,'LEDGER_COMMITTED')
    for path,phase in ((TX,'TRANSACTION_COMMITTED'),(STATE,'STATE_COMMITTED'),(WORKFLOW,'WORKFLOW_COMMITTED')):
        if pinned(path,sha(raw[path]))!=raw[path]: raise ValueError('runtime changed before replacement')
        meta=os.lstat(path); write_file(path,target[path],meta.st_uid,meta.st_gid,stat.S_IMODE(meta.st_mode),True)
        checkpoint(journal,phase)
    snapshot_members={'recovery_controller.py':payloads[SELF],
        'interruption_evidence.json':payloads[INTERRUPTION_EVIDENCE],
        'interruption_report.md':payloads[INTERRUPTION_REPORT]}
    os.mkdir(SNAPSHOT,0o550); os.chown(SNAPSHOT,0,1000)
    for name,data in snapshot_members.items(): write_file(SNAPSHOT/name,data,0,1000,0o440)
    manifest=encode({'schema':'m9-host-shutdown-recovery-snapshot-v1','members':{
        name:{'bytes':len(data),'sha256':sha(data)} for name,data in snapshot_members.items()}})
    write_file(SNAPSHOT/'snapshot_manifest.json',manifest,0,1000,0o440)
    os.chmod(SNAPSHOT,0o550); sync_dir(SNAPSHOT)
    journal['control_elapsed_seconds']=time.monotonic()-started
    checkpoint(journal,'SUCCESS_COMMITTED')
    return {'status':'RECOVERY_SUCCESS_COMMITTED','source_build_authorized':False,
        'elapsed_upper_bound_seconds':ELAPSED,'journal_sha256':sha(pinned(JOURNAL,None)),
        'runtime_sha256':{str(p):sha(pinned(p,None)) for p in (STATE,WORKFLOW,TX,LEDGER)},
        'clean_portable_sha256':canonical(clean_portable)}


def main():
    global ACTIVE_LOCK_FD, ACTIVE_LOCK_IDENTITY
    if (os.geteuid()!=0 or sys.version_info[:3]!=(3,9,23)
            or Path(sys.executable).resolve()!= (ROOT/'env/deeph-v022/bin/python3.9').resolve()
            or not(sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode)):
        raise SystemExit('root frozen Python3.9.23 -I -S -B required')
    action,payloads,reader,budget=authority(sys.argv[1:])
    fd=os.open(LOCK,os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        before=os.fstat(fd)
        fields=('st_dev','st_ino','st_uid','st_gid','st_mode','st_nlink','st_size')
        ACTIVE_LOCK_FD=fd; ACTIVE_LOCK_IDENTITY=tuple(getattr(before,k) for k in fields)
        assert_lock()
        result=validate(action,payloads,reader,budget)
        print(json.dumps(result,sort_keys=True))
    finally:
        ACTIVE_LOCK_FD=None; ACTIVE_LOCK_IDENTITY=None; os.close(fd)


if __name__=='__main__':
    main()
