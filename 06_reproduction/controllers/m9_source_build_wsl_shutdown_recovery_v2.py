"""Pristine-only recovery for the interrupted M9 v4 source_build transaction."""
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
SELF = PROJECT / '06_reproduction/controllers/m9_source_build_wsl_shutdown_recovery_v2.py'
TEST = PROJECT / '06_reproduction/tests/test_m9_source_build_wsl_shutdown_recovery_v2.py'
WORK = AUDITS / 'M9_source_build_wsl_shutdown_recovery_v2_work_package.md'
AUTH = PROJECT / '00_scope/D019_standing_execution_authorization.md'
INTERRUPTION_REPORT = AUDITS / 'M9_source_build_v4_interruption_independent_audit.md'
INTERRUPTION_EVIDENCE = AUDITS / 'M9_source_build_v4_interruption_postexecution_evidence.json'
PREEXECUTION_EVIDENCE = AUDITS / 'M9_source_build_v4_preexecution_evidence.json'
RECEIPTS = PROJECT / '06_reproduction/controllers/m9_py39_consumer_gate_completion.py'
BUDGET = PROJECT / '06_reproduction/scripts/m9_budget.py'
V4_MANIFEST = PROJECT / '06_reproduction/manifests/m9_source_build_v4_frozen_hashes.json'
FROZEN = PROJECT / '06_reproduction/manifests/m9_source_build_wsl_shutdown_recovery_v2_frozen_hashes.json'
INITIAL_REPORT = AUDITS / 'M9_source_build_wsl_shutdown_recovery_v2_implementation_audit.md'
INITIAL_VERDICT = AUDITS / 'M9_source_build_wsl_shutdown_recovery_v2_implementation_verdict.json'
REPORT = AUDITS / 'M9_source_build_wsl_shutdown_recovery_v2_targeted_reaudit.md'
VERDICT = AUDITS / 'M9_source_build_wsl_shutdown_recovery_v2_final_verdict.json'

LOCK = ROOT / 'manifests/budget.lock'
STATE = ROOT / 'manifests/budget_state.json'
WORKFLOW = ROOT / 'manifests/overlap_workflow_state.json'
TX = ROOT / 'manifests/overlap_transaction.json'
LEDGER = ROOT / 'manifests/budget_ledger.jsonl'
CAPABILITY = ROOT / 'manifests/overlap_capabilities/c68a261b9f1e95c692a3b4241360440e.consumed.json'
RECEIPT = ROOT / 'manifests/overlap_capabilities/c68a261b9f1e95c692a3b4241360440e.launcher-receipt.json'
GATE = ROOT / 'manifests/source_build_v4_gate.json'
PERMIT = ROOT / 'manifests/source_build_v4_execution_permit.json'
BUILD = ROOT / 'software/openmx-overlap-build'
CLEAN = ROOT / 'software/openmx-overlap-build.failed-80e28da82f076f4f7b1811f5897216bd.retired'
PRIOR_ARCHIVE = ROOT / 'software/openmx-overlap-build.interrupted-4d7808af7df9418518a59afeba766eb9.retired'
PRIOR_LOG_ARCHIVE = ROOT / 'logs/overlap-build.interrupted-4d7808af7df9418518a59afeba766eb9.retired'
LOGS = ROOT / 'logs/overlap-build'
RECOVERY_ID = 'm9-source-build-wsl-shutdown-recovery-20260902-01'
FAILURE_ID = 'd52575f446d3c62f0fc93c3c65f3c959'
CAPABILITY_ID = 'c68a261b9f1e95c692a3b4241360440e'
ARCHIVE = BUILD.with_name('openmx-overlap-build.interrupted-' + FAILURE_ID + '.retired')
LOG_ARCHIVE = LOGS.with_name('overlap-build.interrupted-' + FAILURE_ID + '.retired')
STAGING = BUILD.with_name(BUILD.name + '.wsl-shutdown-recovery-v2.staging')
PRIVATE = Path('/root/deeph-m9-control/source-build-wsl-shutdown-recovery-v2')
SNAPSHOT = ROOT / 'controls/source-build-wsl-shutdown-recovery-v2'
JOURNAL = PRIVATE / 'journal.json'
SHUTDOWN_UTC = '2026-09-01T14:49:10.512965566Z'
ELAPSED = 138.401802566
RECOVERY_FORECAST = 1073741824
INTERRUPTION_REPORT_SHA = '0bc6d751b11f03f50bb861b143e69116288838dc56765bbc32e52492ad5ce5e4'
INTERRUPTION_EVIDENCE_SHA = '9985eff9ec38d5763ace3ede75eef418ed8d57bbf5f7611025154f992debebbb'
PREEXECUTION_EVIDENCE_SHA = '11c20faeb1069d29804d6ffa5b98705ab6579ced0a62ca7d2b0583eb1c7ecc70'
RECEIPTS_SHA = 'c2c235c444bae0f613078a060efa9733f869533385fa84268bfd2cc2b3c3ef55'
V4_MANIFEST_SHA = '5862155306e595f268e996a9712194faabd2347e94b73a0118ebb403c763cf09'
AUTH_SHA = '4f44e839d2deccf8a4fd172ad9a45243ad446c1009d1f09666f26f2c23ba28e0'
EXPECTED_INTERRUPTED_TREE = '25fa00697f192967f8adcc0656eea976eeb9839390a78757a04d00ac66796dc0'
EXPECTED_CLEAN_TREE = '060012bff89f774648f090271e7c8d1b7f54802954fad51503704569d456a359'
EXPECTED_LOG_TREE = 'f1d69a2016dc0ae5df54519d4155a9b0317bcb7c4edf55cdea85c43d9a4b1db3'
EXPECTED_PRIOR_ARCHIVE = '82bc6705ef8a507d2580630592f4903726622768aebb5bd7b1d22d93afa12515'
EXPECTED_PRIOR_LOG_ARCHIVE = '5ea65a500eaadc665b4d282ce8b8c55019629b722020b7baa73259c9f862d4de'
EXPECTED_GATE_SHA = 'dcd0a0ed3307add49df5b7586ba0bf01b2fc55b0469a42067893e563ba2ff3c1'
EXPECTED_PERMIT_SHA = 'c3aae6ff0c5aaffb3d5a711b48e7dc505061959eb144509995f8e9890f5853d4'
EXPECTED_BUILD_COUNT = 7621
EXPECTED_CLEAN_COUNT = 5319
EXPECTED_PRIOR_ARCHIVE_COUNT = 7640
EXPECTED_LOG_COUNT = 4
EXPECTED_V4_DIRECT_MEMBERS = 22
BUDGET_SHA = 'a94902a942f98217171be5d9967f469a4dd4563c80e6e6ef3d68e6cede71168d'
INITIAL_REPORT_SHA = '3d4d8c1316d0b76404b032393d2cc8dfc8213fe590a566b6c4184b01f37a886e'
INITIAL_VERDICT_SHA = 'bae4b15404359c7e558650b4a73adb8c59e0c4cc0077c510853b1e27e0fd300b'
SOURCE_SET = {SELF, TEST, WORK, AUTH, INTERRUPTION_REPORT, INTERRUPTION_EVIDENCE,
              PREEXECUTION_EVIDENCE, RECEIPTS, BUDGET, V4_MANIFEST,
              INITIAL_REPORT, INITIAL_VERDICT}
PHASES = ('PREPARED', 'INTERRUPTED_ARCHIVED', 'LOGS_ARCHIVED', 'CLEAN_TREE_CLONED',
          'LEDGER_COMMITTED', 'TRANSACTION_COMMITTED', 'STATE_COMMITTED',
          'WORKFLOW_COMMITTED', 'SUCCESS_COMMITTED')
ACTIVE_LOCK_FD = None
ACTIVE_LOCK_IDENTITY = None
PROC = Path('/proc')
CONTROL_UID = 0
CONTROL_GID = 0
SNAPSHOT_GID = 1000


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


def validate_v4_direct_authority(v4_raw):
    root=json.loads(v4_raw)
    if (root.get('schema')!='m9-source-build-frozen-v4'
            or not isinstance(root.get('files'),dict)
            or len(root['files'])!=EXPECTED_V4_DIRECT_MEMBERS):
        raise ValueError('v4 frozen schema differs')
    direct={}
    for name,digest in root['files'].items():
        direct[name]=sha(pinned(Path(name),digest))
    if direct!=root['files']:
        raise ValueError('v4 direct authority closure differs')
    return direct


def authority(argv):
    if len(argv) != 5 or argv[1] not in ('preflight', 'recover'):
        raise ValueError('expected self_sha preflight|recover frozen_sha verdict_sha report_sha; no resume')
    self_sha, action, frozen_sha, verdict_sha, report_sha = argv
    payloads = {FROZEN:pinned(FROZEN,frozen_sha), REPORT:pinned(REPORT,report_sha),
                VERDICT:pinned(VERDICT,verdict_sha)}
    frozen = json.loads(payloads[FROZEN])
    if (set(frozen) != {'schema','files'}
            or frozen['schema'] != 'm9-wsl-shutdown-recovery-frozen-v2'
            or set(frozen['files']) != {str(p) for p in SOURCE_SET}):
        raise ValueError('wsl-shutdown recovery source closure differs')
    for name, digest in frozen['files'].items():
        payloads[Path(name)] = pinned(Path(name), digest)
    if (frozen['files'][str(SELF)] != self_sha
            or sha(payloads[INTERRUPTION_REPORT]) != INTERRUPTION_REPORT_SHA
            or sha(payloads[INTERRUPTION_EVIDENCE]) != INTERRUPTION_EVIDENCE_SHA
            or sha(payloads[PREEXECUTION_EVIDENCE]) != PREEXECUTION_EVIDENCE_SHA
            or sha(payloads[RECEIPTS]) != RECEIPTS_SHA
            or sha(payloads[BUDGET]) != BUDGET_SHA
            or sha(payloads[V4_MANIFEST]) != V4_MANIFEST_SHA
            or sha(payloads[INITIAL_REPORT]) != INITIAL_REPORT_SHA
            or sha(payloads[INITIAL_VERDICT]) != INITIAL_VERDICT_SHA
            or sha(payloads[AUTH]) != AUTH_SHA):
        raise ValueError('wsl-shutdown recovery historical binding differs')
    verdict = json.loads(payloads[VERDICT])
    expected = {'schema':'m9-wsl-shutdown-recovery-implementation-verdict-v2',
        'status':'PASS','blocking':0,'non_blocking':0,'frozen_sha256':frozen_sha,
        'report_path':str(REPORT),'report_sha256':report_sha}
    if verdict != expected or type(verdict['blocking']) is not int or type(verdict['non_blocking']) is not int:
        raise ValueError('wsl-shutdown recovery independent authority differs')
    # Old manifests are immutable historical commitments, not claims that every
    # mutable leaf still has its historical bytes. Seal only the v4 direct closure
    # plus the two explicitly frozen modules that this recovery executes.
    validate_v4_direct_authority(payloads[V4_MANIFEST])
    reader = load_source('m9_wsl_shutdown_receipts', RECEIPTS, payloads[RECEIPTS])
    budget = load_source('m9_wsl_shutdown_budget_readonly', BUDGET, payloads[BUDGET])
    return action, payloads, reader, budget


def formal_roots():
    return (ROOT / 'manifests', ROOT / 'controls', PRIVATE.parent)


def formal_namespace(reader):
    result = {}
    for root in formal_roots():
        result.update(reader.capture_tree(root))
    return result


def decoded_formal(evidence):
    item = evidence['formal_namespace']
    raw = gzip.decompress(base64.b64decode(item['canonical_json_gzip_base64'], validate=True))
    if len(raw) != item['canonical_json_bytes'] or sha(raw) != item['canonical_sha256']:
        raise ValueError('interruption namespace payload differs')
    value = json.loads(raw)
    if canonical(value) != item['canonical_sha256'] or len(value) != 275 or item['count'] != 275:
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


def is_beneath(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def related_build_processes(capability):
    expected = []
    for field in ('budget_argv','launcher_argv'):
        expected.append(b'\0'.join(str(x).encode() for x in capability[field]) + b'\0')
    anchors = tuple(str(value).encode() for value in (
        BUILD, LOGS, FAILURE_ID, CAPABILITY_ID,
        ROOT / 'controls/source-build-v4/m9_source_build_v4_consumer.py',
        ROOT / 'controls/source-build-v4/m9_source_build_v4_launcher.py'))
    tool_names = {'configure','make','gmake','gcc','g++','c++','cc','gfortran','ld','ar',
                  'ranlib','mpicc','mpicxx','mpic++','mpif77','mpif90','mpifort',
                  'opal_wrapper','openmx','mpirun','mpiexec','orterun'}
    matches = []
    for entry in PROC.iterdir():
        if not entry.name.isdecimal():
            continue
        try:
            raw = (entry / 'cmdline').read_bytes()
        except (FileNotFoundError, ProcessLookupError):
            continue
        except PermissionError as error:
            raise ValueError('cannot prove process unrelated: unreadable cmdline '+entry.name) from error
        if not raw:
            continue
        args = [item for item in raw.split(b'\0') if item]
        command = Path(os.fsdecode(args[0])).name if args else ''
        reasons = []
        if raw in expected or any(value in raw for value in expected):
            reasons.append('authorized-chain-argv')
        if any(anchor in raw for anchor in anchors):
            reasons.append('frozen-build-anchor')
        links = {}
        vanished = False
        for field in ('cwd','exe'):
            try:
                links[field] = Path(os.readlink(entry / field))
            except (FileNotFoundError, ProcessLookupError):
                vanished = True
                break
            except PermissionError as error:
                raise ValueError('cannot prove process unrelated: unreadable '+field+' '+entry.name) from error
        if vanished:
            continue
        if is_beneath(links['cwd'], BUILD) or is_beneath(links['cwd'], LOGS):
            reasons.append('build-working-directory')
        if is_beneath(links['exe'], BUILD):
            reasons.append('build-tree-executable')
        if command in tool_names and (is_beneath(links['cwd'], BUILD)
                                      or is_beneath(links['exe'], BUILD)):
            reasons.append('build-tool')
        if reasons:
            matches.append({'pid':int(entry.name),'argv_sha256':sha(raw),
                            'command':command,'cwd':str(links['cwd']),
                            'exe':str(links['exe']),'reasons':sorted(set(reasons))})
    return sorted(matches,key=lambda item:item['pid'])


def process_alive(capability):
    return bool(related_build_processes(capability))


def raw_runtime(evidence):
    result = {}
    for name, value in evidence['runtime_raw'].items():
        raw = gzip.decompress(base64.b64decode(value['gzip_base64'], validate=True))
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
            or tx.get('action') != 'source_build' or tx.get('child_pid') != 397
            or tx.get('start_utc') != '2026-09-01T14:46:52.111163Z'):
        raise ValueError('orphaned transaction semantics differ')
    old_cpu = float(state['cpu_seconds']['overlap_build'])
    if old_cpu != 7507.245045788001:
        raise ValueError('orphaned transaction accounting parent differs')
    state['cpu_seconds']['overlap_build'] = old_cpu + ELAPSED
    state['active_overlap_transaction'] = None
    state['last_event_utc'] = SHUTDOWN_UTC
    state['recovered_from_source_build_wsl_shutdown'] = RECOVERY_ID
    workflow['active_transaction'] = None
    workflow['hard_stopped'] = False
    workflow['stage'] = 'SOURCES_PREPARED'
    workflow['recovered_from_source_build_wsl_shutdown'] = RECOVERY_ID
    tx.update({'state':'FAILED_COMMITTED','end_utc':SHUTDOWN_UTC,
        'elapsed_seconds':ELAPSED,'elapsed_semantics':'conservative_wall_upper_bound_not_measured_cpu',
        'exit_code':None,'timed_out':False,'reasons':['wsl_shutdown_external_interruption'],
        'launcher_receipt_sha256':None,'recovery_id':RECOVERY_ID,
        'interruption_report_sha256':INTERRUPTION_REPORT_SHA,
        'interruption_evidence_sha256':INTERRUPTION_EVIDENCE_SHA,
        'interrupted_build_tree_sha256':EXPECTED_INTERRUPTED_TREE,
        'interrupted_log_tree_sha256':EXPECTED_LOG_TREE})
    event = {'event':'SOURCE_BUILD_WSL_SHUTDOWN_RECOVERY','event_id':RECOVERY_ID,
        'utc':SHUTDOWN_UTC,'parent_transaction_id':FAILURE_ID,
        'parent_transaction_sha256':sha(raw[TX]),'ledger_prefix_sha256':sha(raw[LEDGER]),
        'ledger_prefix_bytes':len(raw[LEDGER]),'elapsed_seconds':ELAPSED,
        'elapsed_semantics':'conservative_wall_upper_bound_not_measured_cpu',
        'cpu_seconds':state['cpu_seconds'],'gpu_seconds':state['gpu_seconds'],
        'cpu_adjustments':state['cpu_adjustments'],'source_build_authorized':False,
        'authorization':{'d019_sha256':sha(payloads[AUTH]),
            'interruption_report_sha256':sha(payloads[INTERRUPTION_REPORT]),
            'interruption_evidence_sha256':sha(payloads[INTERRUPTION_EVIDENCE]),
            'preexecution_evidence_sha256':sha(payloads[PREEXECUTION_EVIDENCE]),
            'v4_manifest_sha256':sha(payloads[V4_MANIFEST]),
            'frozen_sha256':sha(payloads[FROZEN]),'implementation_report_sha256':sha(payloads[REPORT]),
            'implementation_verdict_sha256':sha(payloads[VERDICT])}}
    line = (json.dumps(event,ensure_ascii=False,sort_keys=True)+'\n').encode('utf-8')
    return {STATE:encode(state),WORKFLOW:encode(workflow),TX:encode(tx),LEDGER:raw[LEDGER]+line},event,line


def require_pristine():
    forbidden = (ARCHIVE,LOG_ARCHIVE,STAGING,PRIVATE,SNAPSHOT,
        STATE.with_name(STATE.name+'.wsl-shutdown-recovery-v2.tmp'),
        WORKFLOW.with_name(WORKFLOW.name+'.wsl-shutdown-recovery-v2.tmp'),
        TX.with_name(TX.name+'.wsl-shutdown-recovery-v2.tmp'))
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


def ensure_owner(path,uid,gid,follow_symlinks=True):
    current=os.stat(path,follow_symlinks=follow_symlinks)
    if (current.st_uid,current.st_gid)!=(uid,gid):
        os.chown(path,uid,gid,follow_symlinks=follow_symlinks)


def write_file(path,raw,uid=None,gid=None,mode=0o600,replace=False):
    if uid is None: uid=CONTROL_UID
    if gid is None: gid=CONTROL_GID
    temporary = path.with_name(path.name+'.wsl-shutdown-recovery-v2.tmp') if replace else path
    if os.path.lexists(temporary):
        raise FileExistsError(str(temporary))
    fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,mode)
    try:
        current=os.fstat(fd)
        if (current.st_uid,current.st_gid)!=(uid,gid): os.fchown(fd,uid,gid)
        os.fchmod(fd,mode)
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
    ensure_owner(destination,meta.st_uid,meta.st_gid,follow_symlinks=False)
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
        meta=src.stat(); ensure_owner(dst,meta.st_uid,meta.st_gid); shutil.copystat(src,dst)
    meta=source.stat(); ensure_owner(destination,meta.st_uid,meta.st_gid); shutil.copystat(source,destination)
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
    capability_evidence=evidence['capability']
    capability_receipt=reader.filesystem_receipt(CAPABILITY)
    if (capability!=capability_evidence['content']
            or capability_receipt!=capability_evidence['consumed_receipt']
            or capability.get('state')!='CONSUMED'
            or capability.get('capability_id')!=CAPABILITY_ID or os.path.lexists(RECEIPT)
            or process_present or not capability_evidence['bound_path_absent']
            or not capability_evidence['launcher_receipt_absent']):
        raise ValueError('consumed capability or orphan process semantics differ')
    gate_raw=pinned(GATE,EXPECTED_GATE_SHA)
    permit_raw=pinned(PERMIT,None)
    if (sha(permit_raw)!=EXPECTED_PERMIT_SHA
            or evidence['authority']['v4_gate_sha256']!=EXPECTED_GATE_SHA
            or evidence['authority']['v4_permit_sha256']!=EXPECTED_PERMIT_SHA):
        raise ValueError('v4 gate or permit drift')
    interrupted_receipts=reader.capture_tree(BUILD)
    clean_receipts=reader.capture_tree(CLEAN)
    prior_receipts=reader.capture_tree(PRIOR_ARCHIVE)
    prior_log_receipts=reader.capture_tree(PRIOR_LOG_ARCHIVE)
    if (canonical(interrupted_receipts)!=EXPECTED_INTERRUPTED_TREE
            or len(interrupted_receipts)!=evidence['trees']['build']['count']):
        raise ValueError('interrupted build tree drift')
    if canonical(clean_receipts)!=EXPECTED_CLEAN_TREE:
        raise ValueError('clean historical tree drift')
    if (canonical(prior_receipts)!=EXPECTED_PRIOR_ARCHIVE
            or len(prior_receipts)!=evidence['trees']['prior_interrupted_archive']['count']
            or canonical(prior_log_receipts)!=EXPECTED_PRIOR_LOG_ARCHIVE
            or len(prior_log_receipts)!=evidence['trees']['prior_log_archive']['count']):
        raise ValueError('prior archive tree drift')
    interrupted_portable=portable_receipts(interrupted_receipts,BUILD)
    clean_portable=portable_receipts(clean_receipts,CLEAN)
    if clean_portable==interrupted_portable:
        raise ValueError('interrupted tree unexpectedly pristine')
    log_receipts=reader.capture_tree(LOGS)
    log_evidence=evidence['trees']['current_logs']
    if (canonical(log_receipts)!=EXPECTED_LOG_TREE
            or len(log_receipts)!=log_evidence['count']):
        raise ValueError('interrupted log tree drift')
    log_paths={str(LOGS),*(log_evidence['raw_files'])}
    if set(log_receipts)!=log_paths:
        raise ValueError('interrupted log path closure differs')
    for name,wanted in log_evidence['raw_files'].items():
        data=pinned(Path(name),wanted['sha256'])
        if len(data)!=wanted['bytes']:
            raise ValueError('interrupted log bytes differ')
    products={}
    for name,present in evidence['products']['expected_final_products_present'].items():
        products[name]=os.path.lexists(name)
        if present or products[name]: raise ValueError('forbidden interrupted product appeared')
    issues=budget.violations(json.loads(raw[STATE]),RECOVERY_FORECAST)
    if issues:
        raise ValueError('wsl-shutdown recovery storage forecast rejected: '+repr(issues))
    storage=(budget.storage_snapshot(json.loads(raw[STATE]))
             if hasattr(budget,'storage_snapshot') else None)
    assert_lock()
    return {'formal':current_formal,'raw_sha256':{str(p):sha(v) for p,v in raw.items()},
        'capability_sha256':sha(capability_raw),'capability':capability,
        'capability_receipt':capability_receipt,
        'process_present':process_present,'receipt_present':os.path.lexists(RECEIPT),
        'gate_sha256':sha(gate_raw),'permit_sha256':sha(permit_raw),
        'interrupted_receipts':interrupted_receipts,
        'interrupted_portable':interrupted_portable,'clean_receipts':clean_receipts,
        'clean_portable':clean_portable,'prior_receipts':prior_receipts,
        'prior_log_receipts':prior_log_receipts,'log_paths':sorted(log_paths),
        'log_receipts':log_receipts,'products_present':products,
        'budget_violations':list(issues),'storage_snapshot':storage}


def validate(action,payloads,reader,budget):
    assert_lock()
    evidence=json.loads(payloads[INTERRUPTION_EVIDENCE])
    classification=evidence.get('classification',{})
    acceptance=evidence.get('recovery_acceptance',{})
    trees=evidence.get('trees',{})
    if (evidence.get('schema')!='m9-source-build-v4-interruption-postexecution-evidence-v1'
            or classification.get('verdict')!='FAIL' or classification.get('blocking')!=1
            or classification.get('non_blocking')!=0
            or classification.get('blocking_id')!='M9-SB-V4-INT-B01'
            or not classification.get('external_wsl_instance_interruption_nonterminal')
            or classification.get('ordinary_budget_failure_committed')
            or classification.get('windows_full_shutdown_is_same_event')
            or evidence.get('formal_namespace',{}).get('count')!=275
            or evidence.get('timeline',{}).get('conservative_wall_upper_bound_seconds')!=ELAPSED
            or evidence.get('timeline',{}).get('upper_bound_end_utc')!=SHUTDOWN_UTC
            or trees.get('build',{}).get('canonical_sha256')!=EXPECTED_INTERRUPTED_TREE
            or trees.get('build',{}).get('count')!=EXPECTED_BUILD_COUNT
            or trees.get('current_logs',{}).get('canonical_sha256')!=EXPECTED_LOG_TREE
            or trees.get('current_logs',{}).get('count')!=EXPECTED_LOG_COUNT
            or trees.get('retired_clean',{}).get('canonical_sha256')!=EXPECTED_CLEAN_TREE
            or trees.get('retired_clean',{}).get('count')!=EXPECTED_CLEAN_COUNT
            or trees.get('prior_interrupted_archive',{}).get('canonical_sha256')!=EXPECTED_PRIOR_ARCHIVE
            or trees.get('prior_interrupted_archive',{}).get('count')!=EXPECTED_PRIOR_ARCHIVE_COUNT
            or trees.get('prior_log_archive',{}).get('canonical_sha256')!=EXPECTED_PRIOR_LOG_ARCHIVE
            or trees.get('prior_log_archive',{}).get('count')!=EXPECTED_LOG_COUNT
            or evidence.get('authority',{}).get('preexecution_evidence_sha256')!=PREEXECUTION_EVIDENCE_SHA
            or evidence.get('processes',{}).get('matched_build_processes')!=[]
            or not evidence.get('products',{}).get('hdf5_partial_intermediates_present')
            or evidence.get('products',{}).get('openmx_compile_started')
            or acceptance.get('must_charge_controller_compatible_wall_upper_bound_seconds')!=ELAPSED
            or acceptance.get('must_bind_build_tree_sha256')!=EXPECTED_INTERRUPTED_TREE
            or acceptance.get('must_bind_current_logs_sha256')!=EXPECTED_LOG_TREE
            or acceptance.get('must_bind_complete_275_formal_namespace_sha256')
               != evidence['formal_namespace']['canonical_sha256']
            or acceptance.get('must_preserve_consumed_capability_sha256')
               != evidence['capability']['consumed_receipt']['sha256']):
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
    os.mkdir(PRIVATE,0o700); ensure_owner(PRIVATE,CONTROL_UID,CONTROL_GID); os.chmod(PRIVATE,0o700); sync_dir(PRIVATE.parent)
    for path,data in sorted(payloads.items(),key=lambda item:str(item[0])):
        write_file(PRIVATE/path.name,data)
    for path,data in raw.items(): write_file(PRIVATE/('before-'+path.name),data)
    journal={'schema':'m9-source-build-wsl-shutdown-recovery-journal-v2',
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
    os.mkdir(SNAPSHOT,0o750); ensure_owner(SNAPSHOT,CONTROL_UID,SNAPSHOT_GID)
    for name,data in snapshot_members.items(): write_file(SNAPSHOT/name,data,CONTROL_UID,SNAPSHOT_GID,0o440)
    manifest=encode({'schema':'m9-wsl-shutdown-recovery-snapshot-v2','members':{
        name:{'bytes':len(data),'sha256':sha(data)} for name,data in snapshot_members.items()}})
    write_file(SNAPSHOT/'snapshot_manifest.json',manifest,CONTROL_UID,SNAPSHOT_GID,0o440)
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
