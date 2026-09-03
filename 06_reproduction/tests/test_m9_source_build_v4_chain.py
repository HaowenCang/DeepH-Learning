"""V4-specific chain regression. All writes are temporary; no compilation."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import types
import unittest
from unittest import mock


HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


t = load('v4_chain_fixtures', HERE / 'test_m9_source_build_v4_consumer.py')
c, i = t.c, t.i
LAUNCHER_PATH = c.LAUNCHER
l = load('v4_chain_launcher', LAUNCHER_PATH)
REPAIR_PATH = c.REPAIR
DRIVER_PATH = c.DRIVER
COMMON_PATH = c.PROJECT / '06_reproduction/scripts/m9_overlap_common.py'
COMMON_SHA = 'fc8c16ed37072c6410c1d4bc942716fad66be4d3d22c2f72cc299b7fce55e07f'


class ChainTests(unittest.TestCase):
    def fixture(self):
        f = t.Fixture(); self.addCleanup(f.close); return f

    def actual_installed_fixture(self, chain=False, failure=False):
        """Relocate only fixture constants before freezing an actual snapshot.

        Child processes receive no monkeypatches or injected sys.path. This is
        still a temporary fixture, not a formal installation fact audit.
        """
        f = self.fixture()
        if chain:
            mapping={str(COMMON_PATH):COMMON_SHA,str(DRIVER_PATH):c.DRIVER_BASE_SHA}
            t.jwrite(c.OLD_OVERLAP_MANIFEST,{'files':mapping})
            c.OLD_MANIFESTS[c.OLD_OVERLAP_MANIFEST]=c.sha(c.OLD_OVERLAP_MANIFEST.read_bytes())
            directory=c.ROOT/'manifests/overlap_capabilities'
            directory.mkdir();os.chown(directory,1000,1000);os.chmod(directory,0o700)
            os.chown(c.ROOT/'manifests/overlap_transaction.json',1000,1000)
        paths = {k: str(v) for k, v in f.overrides.items()}
        values = {k: getattr(c, k) for k in ['PREPARED_SHA','RETIRED_SHA','EVIDENCE_SHA','FACT_SHA',
                                            'OLD_INSTALL_VERDICT_SHA','OLD_V3_INSTALL_VERDICT_SHA',
                                            'LOCK_EXPECTED']}
        settings = {'paths':paths, 'values':values, 'sources':[str(p) for p in c.SOURCE_PATHS],
                    'old':{str(p):v for p,v in c.OLD_MANIFESTS.items()},
                    'runtime':list(c.MUTABLE_RUNTIME), 'forbidden':[str(p) for p in c.FORBIDDEN_PRODUCTS]}
        suffix = '\n_fixture = json.loads(' + repr(json.dumps(settings)) + ')\n'
        suffix += "for _k,_v in _fixture['paths'].items(): globals()[_k]=Path(_v)\n"
        suffix += "for _k,_v in _fixture['values'].items(): globals()[_k]=_v\n"
        suffix += "LOCK_EXPECTED=tuple(LOCK_EXPECTED)\nSOURCE_PATHS={Path(p) for p in _fixture['sources']}\n"
        suffix += "OLD_MANIFESTS={Path(p):v for p,v in _fixture['old'].items()}\n"
        suffix += "MUTABLE_RUNTIME=set(_fixture['runtime'])\nFORBIDDEN_PRODUCTS=[Path(p) for p in _fixture['forbidden']]\n"
        if chain:
            # A fixture issuer models the native capability format and live argv.
            # The actual budget post-child state machine is tested separately.
            suffix += r'''
def _fixture_parent():
    import subprocess
    fixed_runtime();require_argv(sys.argv[1:])
    capability_id='1'*32;transaction_id='2'*32
    child_argv=[str(PYTHON.resolve()),'-I','-S','-B',str(SNAPSHOT/LAUNCHER.name),'--capability-id',capability_id]
    process=subprocess.Popen(child_argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    tx={'schema_version':'m9-overlap-transaction-v1','state':'RUNNING','transaction_id':transaction_id,'child_pid':process.pid}
    (ROOT/'manifests/overlap_transaction.json').write_text(json.dumps(tx),encoding='utf-8')
    value={'schema_version':'m9-overlap-capability-v1','state':'BOUND','capability_id':capability_id,
        'transaction_id':transaction_id,'child_pid':process.pid,'budget_pid':os.getpid(),
        'budget_argv':[x.decode() for x in Path('/proc/self/cmdline').read_bytes().split(b'\0') if x],
        'launcher_argv':child_argv,'action':'source_build','structure_id':None,'bucket':'overlap_build',
        'forecast_bytes':4294967296,'budget_bootstrap':{'fixture':'live-parent'}}
    path=ROOT/'manifests/overlap_capabilities'/(capability_id+'.json')
    fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as stream:json.dump(value,stream)
    try:out,err=process.communicate(timeout=20)
    except BaseException:
        process.kill();process.communicate();raise
    if process.returncode:
        try:validate_launcher_receipt(capability_id,transaction_id,value['budget_bootstrap'])
        except ValueError:pass
        else:raise AssertionError('failed child receipt was accepted')
        print(json.dumps({'child_rc':process.returncode,'stderr':err.decode(),'parent_rejected':True}))
        return 0
    digest=validate_launcher_receipt(capability_id,transaction_id,value['budget_bootstrap'])
    print(json.dumps({'child_rc':0,'child':json.loads(out),'receipt_sha256':digest}))
    return 0
'''
        consumer_source = t.REAL_CONSUMER.decode().replace("\nif __name__ == '__main__':",suffix+"\nif __name__ == '__main__':")
        if chain:consumer_source=consumer_source.replace('raise SystemExit(main())','raise SystemExit(_fixture_parent())')
        launcher_suffix = '\nSNAPSHOT = Path(' + repr(str(c.SNAPSHOT)) + ')\n'
        if chain:
            launcher_suffix += '\nCAPABILITY_ROOT = Path(' + repr(str(c.ROOT/'manifests/overlap_capabilities')) + ')\n'
            launcher_suffix += '_fixture_workflow_lock=Path(' + repr(str(c.ROOT/'manifests/overlap_workflow.lock')) + ')\n'
            launcher_suffix += '_fixture_failure=' + repr(failure) + '\n'
            launcher_suffix += r'''
_fixture_original_exec=FrozenSourceLoader.exec_module
def _fixture_exec(self,module):
    _fixture_original_exec(self,module)
    if self.fullname=='m9_overlap_common':module.WORKFLOW_LOCK=_fixture_workflow_lock
    if self.fullname=='m9_openmx_build':
        def _read_only_compute_leaf(contract):
            context=module.require_budget_context('overlap_build',('source_build',))
            assert context['state']=='CONSUMED' and context['child_pid']==os.getpid()
            assert module.require_budget_context.__globals__ is sys.modules['m9_overlap_common'].__dict__
            if _fixture_failure:raise RuntimeError('fixture compute leaf failure')
            module.verify_packages(contract)
            return {'test_only':True,'consumed_context':True,'build_executed':False}
        module.build_sources=_read_only_compute_leaf
FrozenSourceLoader.exec_module=_fixture_exec
'''
        launcher_source = t.REAL_LAUNCHER.decode().replace('\nif __name__ == "__main__":', launcher_suffix+'\nif __name__ == "__main__":')
        t.write(c.PROJECT_CONSUMER,consumer_source.encode());t.write(c.LAUNCHER,launcher_source.encode())
        f.frozen = {'schema':'m9-source-build-frozen-v4','files':{str(p):c.sha(p.read_bytes()) for p in c.SOURCE_PATHS}}
        t.jwrite(c.FROZEN,f.frozen)
        f.verdict['frozen_sha256']=c.sha(c.FROZEN.read_bytes());t.jwrite(c.VERDICT,f.verdict)
        installed_verdict=dict(f.verdict,schema='m9-source-build-installation-verdict-v4',
            report_path=str(c.INSTALL_REPORT),report_sha256=c.sha(c.INSTALL_REPORT.read_bytes()))
        t.jwrite(c.INSTALL_VERDICT,installed_verdict)
        payloads={p.name:p.read_bytes() for p in c.SOURCE_PATHS|{c.FROZEN,c.REPORT,c.VERDICT}}
        payloads['m9_budget_source_build.py']=c.derive_budget(t.BASE)
        for name,data in payloads.items():t.write(c.SNAPSHOT/name,data,0o440)
        manifest={'schema':'m9-source-build-snapshot-v4','members':{name:{'bytes':len(data),'sha256':c.sha(data)} for name,data in payloads.items()}}
        t.write(c.SNAPSHOT/'snapshot_manifest.json',i.json_bytes(manifest),0o440)
        f.gate.update(frozen_sha256=c.sha(c.FROZEN.read_bytes()),snapshot_sha256=c.sha(i.json_bytes(manifest)),verdict_sha256=c.sha(c.VERDICT.read_bytes()))
        t.jwrite(c.GATE,f.gate,0o640)
        f.permit.update(gate_sha256=c.sha(c.GATE.read_bytes()),verdict_sha256=c.sha(c.INSTALL_VERDICT.read_bytes()))
        t.jwrite(c.PERMIT,f.permit,0o640)
        return f

    def test_real_uid_installed_launcher_loads_actual_consumer_and_authority(self):
        f=self.actual_installed_fixture();before=f.reader.capture_tree(c.ROOT)
        program="""import importlib.util,json,sys
p=sys.argv[1];s=importlib.util.spec_from_file_location('actual_installed_launcher',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
print(json.dumps(m.installed_authority(),sort_keys=True))
"""
        argv=['/usr/sbin/runuser','-u','evan-williams','--',str(c.PYTHON),'-I','-S','-B','-c',program,str(c.SNAPSHOT/c.LAUNCHER.name)]
        result=subprocess.run(argv,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout),c.execution_binding())
        self.assertEqual(before,f.reader.capture_tree(c.ROOT))
        c.PERMIT.unlink();before=f.reader.capture_tree(c.ROOT)
        missing=subprocess.run(argv,capture_output=True,text=True)
        self.assertEqual(missing.returncode,1);self.assertIn(str(c.PERMIT),missing.stderr)
        self.assertEqual(before,f.reader.capture_tree(c.ROOT))

    def test_actual_installed_consumer_main_readonly_entrypoint(self):
        f=self.actual_installed_fixture();before=f.reader.capture_tree(c.ROOT)
        result=subprocess.run(['/usr/sbin/runuser','-u','evan-williams','--',str(c.PYTHON),'-I','-S','-B',
            str(c.SNAPSHOT/c.PROJECT_CONSUMER.name),'verify-execution'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'],'PASS')
        self.assertEqual(before,f.reader.capture_tree(c.ROOT))

    def test_live_bound_common_derived_driver_receipt_and_parent_chain(self):
        f=self.actual_installed_fixture(chain=True)
        result=subprocess.run(['/usr/sbin/runuser','-u','evan-williams','--',str(c.PYTHON),'-I','-S','-B',
            str(c.SNAPSHOT/c.PROJECT_CONSUMER.name),*c.RUN_ARGV],capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        value=json.loads(result.stdout)
        self.assertEqual(value['child_rc'],0,value)
        self.assertTrue(value['child']['result']['consumed_context'])
        self.assertFalse(value['child']['result']['build_executed'])
        receipt=value['child']['launcher_receipt']
        self.assertEqual(receipt['loaded_sources']['m9_openmx_build']['sha256'],c.DRIVER_DERIVED_SHA)
        self.assertEqual(receipt['v4_binding'],c.execution_binding())
        self.assertEqual(c.validate_launcher_receipt('1'*32,'2'*32,{'fixture':'live-parent'}),value['receipt_sha256'])
        directory=c.ROOT/'manifests/overlap_capabilities'
        self.assertFalse((directory/('1'*32+'.json')).exists())
        self.assertEqual(json.loads((directory/('1'*32+'.consumed.json')).read_bytes())['state'],'CONSUMED')

    def test_live_child_failure_keeps_consumed_and_fail_receipt(self):
        f=self.actual_installed_fixture(chain=True,failure=True)
        result=subprocess.run(['/usr/sbin/runuser','-u','evan-williams','--',str(c.PYTHON),'-I','-S','-B',
            str(c.SNAPSHOT/c.PROJECT_CONSUMER.name),*c.RUN_ARGV],capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        value=json.loads(result.stdout);self.assertNotEqual(value['child_rc'],0);self.assertTrue(value['parent_rejected'])
        directory=c.ROOT/'manifests/overlap_capabilities'
        self.assertEqual(json.loads((directory/('1'*32+'.consumed.json')).read_bytes())['state'],'CONSUMED')
        receipt=json.loads((directory/('1'*32+'.launcher-receipt.json')).read_bytes())
        self.assertEqual(receipt['status'],'FAIL');self.assertIn('fixture compute leaf failure',receipt['error'])

    def test_actual_loader_keeps_common_context_and_derives_only_build(self):
        repair = load('v4_test_repair', REPAIR_PATH)
        prior = {name: sys.modules.get(name) for name in l.LOCAL_MODULES}
        try:
            with mock.patch.object(l, 'CONSUMER', c), mock.patch.object(l, 'REPAIR', repair):
                for name, path, digest in [('m9_overlap_common', COMMON_PATH, COMMON_SHA),
                                          ('m9_openmx_build', DRIVER_PATH, c.DRIVER_BASE_SHA)]:
                    loader = l.FrozenSourceLoader(name, path, digest)
                    spec = importlib.util.spec_from_loader(name, loader, origin=str(path))
                    module = importlib.util.module_from_spec(spec); sys.modules[name] = module
                    loader.exec_module(module)
                    if name == 'm9_overlap_common':
                        common = module
                        sentinel = {'fixture': 'already-consumed-context'}
                        common._BUDGET_CONTEXT = sentinel
                self.assertIs(sys.modules['m9_overlap_common'], common)
                self.assertIs(module.require_budget_context.__globals__['_BUDGET_CONTEXT'], sentinel)
                self.assertEqual(l.LOADED_SOURCES['m9_openmx_build']['sha256'], c.DRIVER_DERIVED_SHA)
                self.assertEqual(l.LOADED_SOURCES['m9_openmx_build']['base_sha256'], c.DRIVER_BASE_SHA)
                self.assertEqual(l.LOADED_SOURCES['m9_overlap_common']['sha256'], COMMON_SHA)
                self.assertFalse(l.LOADED_SOURCES['m9_openmx_build']['bytecode_consulted'])
                with self.assertRaises(RuntimeError): module.build_sources({})
        finally:
            for name, value in prior.items():
                if value is None: sys.modules.pop(name, None)
                else: sys.modules[name] = value

    def test_real_uid1000_v4_loader_complete_toolchain_readonly(self):
        # Real new loader, actual repaired package verifier. No capability or build.
        program = r'''import importlib.util,json,os,sys
from pathlib import Path
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
l=load('launcher_under_test',sys.argv[1]);c=load('consumer_under_test',sys.argv[2]);r=load('repair_under_test',sys.argv[3])
assert os.geteuid()==1000
c.fixed_runtime();l.CONSUMER=c;l.REPAIR=r
for name,path,digest in [('m9_overlap_common',r.COMMON,r.COMMON_SHA),('m9_openmx_build',r.BASE,r.BASE_SHA)]:
 loader=l.FrozenSourceLoader(name,path,digest);s=importlib.util.spec_from_loader(name,loader,origin=str(path));m=importlib.util.module_from_spec(s);sys.modules[name]=m;loader.exec_module(m)
 if name=='m9_overlap_common':
  common=m;sentinel={'test':'no-build-capability'};common._BUDGET_CONTEXT=sentinel
assert m.require_budget_context.__globals__['_BUDGET_CONTEXT'] is sentinel
result=m.verify_packages(json.loads(c.read_bytes(r.CONTRACT,r.CONTRACT_SHA)))
print(json.dumps({'status':'PASS','build_executed':False,'loaded_sources':l.LOADED_SOURCES,'packages':result},sort_keys=True))
'''
        result = subprocess.run(['/usr/sbin/runuser', '-u', 'evan-williams', '--', str(c.PYTHON),
            '-I', '-S', '-B', '-c', program, str(LAUNCHER_PATH), str(t.CONSUMER_PATH), str(REPAIR_PATH)],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads(result.stdout)
        self.assertEqual(value['status'], 'PASS'); self.assertFalse(value['build_executed'])
        self.assertEqual(value['loaded_sources']['m9_openmx_build']['sha256'], c.DRIVER_DERIVED_SHA)

    def test_no_installed_authority_no_load_and_project_cli_no_execution(self):
        loader = l.FrozenSourceLoader('m9_openmx_build', DRIVER_PATH, c.DRIVER_BASE_SHA)
        with mock.patch.object(l, 'CONSUMER', None), self.assertRaises(ImportError):
            loader.exec_module(types.ModuleType('not_executed'))
        with self.assertRaises(RuntimeError): l.installed_authority()

    def test_budget_uses_new_launcher_and_receipt_validator(self):
        b = c.load_bytes('v4_actual_budget', c.OLD_BUDGET, c.derive_budget(t.BASE))
        c.guard_budget(b)
        self.assertEqual(b.OVERLAP_SOURCE_LAUNCHER, c.SNAPSHOT / c.LAUNCHER.name)
        self.assertIs(b.validate_launcher_receipt, c.validate_launcher_receipt)
        self.assertEqual(c.sha(c.derive_budget(t.BASE)), c.DERIVED_SHA)

    def test_recovered_failure_is_required_not_forged_success(self):
        f = self.fixture()
        original_history = c.runtime_and_history
        # Hold receipts constant only to reach semantic checks independently.
        with mock.patch.object(c, 'runtime_and_history', return_value=f.runtime):
            for value in [dict(state='SUCCESS_COMMITTED',action='source_prepare',transaction_id='dc75dda112af553377a697f629801782'),
                          dict(state='FAILED_COMMITTED',action='source_build',transaction_id='0'*32)]:
                t.jwrite(c.ROOT / 'manifests/overlap_transaction.json', value)
                with self.assertRaisesRegex(SystemExit, 'terminal state'): c.verify_gate(False)

    def test_missing_recovery_marker_rejected(self):
        f = self.fixture()
        with mock.patch.object(c, 'runtime_and_history', return_value=f.runtime):
            path = c.ROOT / 'manifests/budget_state.json'
            value = json.loads(path.read_bytes()); value.pop('recovered_from_source_build_host_shutdown')
            t.jwrite(path, value)
            with self.assertRaisesRegex(SystemExit, 'terminal state'): c.verify_gate(False)

    def receipt_fixture(self):
        f = self.fixture()
        capability_id, transaction_id = '1'*32, '2'*32
        bootstrap = {'fixture': 'budget-bootstrap'}
        binding = c.execution_binding()
        parent = [str(c.PYTHON.resolve()), '-I', '-S', '-B', str(c.SNAPSHOT/c.PROJECT_CONSUMER.name), *c.RUN_ARGV]
        child = [str(c.PYTHON.resolve()), '-I', '-S', '-B', str(c.SNAPSHOT/c.LAUNCHER.name), '--capability-id', capability_id]
        consumed = dict(schema_version='m9-overlap-capability-v1', state='CONSUMED', capability_id=capability_id,
                        transaction_id=transaction_id, action='source_build', structure_id=None,
                        bucket='overlap_build', forecast_bytes=4294967296,
                        budget_bootstrap=bootstrap, budget_argv=parent, launcher_argv=child)
        sources = {}
        mapping = {}
        for name, digest in [('m9_overlap_common',COMMON_SHA), ('m9_openmx_build',c.DRIVER_DERIVED_SHA)]:
            path = str(c.DRIVER.parent / (name + '.py'))
            sources[name] = dict(path=path, origin=path, sha256=digest, loader='FrozenSourceLoader', bytecode_consulted=False)
            mapping[path] = digest
            if name == 'm9_openmx_build':
                sources[name]['base_sha256'] = c.DRIVER_BASE_SHA; mapping[path] = c.DRIVER_BASE_SHA
        receipt = dict(schema_version='m9-overlap-source-launcher-receipt-v1', status='PASS',
            capability_id=capability_id, transaction_id=transaction_id, budget_bootstrap=bootstrap, v4_binding=binding,
            launcher_bootstrap=dict(isolated=True,no_site=True,dont_write_bytecode=True,
                modules={name:{} for name in ['argparse','hashlib','json','pathlib']}, python_executable=str(c.PYTHON.resolve())),
            dependency_path=dict(path=str(c.PYTHON.parent.parent/'lib/python3.9/site-packages'),
                added_after_capability=True,method='sys.path.append',site_addsitedir_called=False,pth_processed=False),
            loaded_sources=sources)
        directory = c.ROOT/'manifests/overlap_capabilities'
        rp = directory/(capability_id+'.launcher-receipt.json'); cp=directory/(capability_id+'.consumed.json')
        # Static authority is separately exercised on a complete real fixture.
        f.stack.enter_context(mock.patch.object(c,'execution_binding',return_value=binding))
        t.jwrite(c.OLD_OVERLAP_MANIFEST, {'files':mapping})
        f.stack.enter_context(mock.patch.dict(c.OLD_MANIFESTS,{c.OLD_OVERLAP_MANIFEST:c.sha(c.OLD_OVERLAP_MANIFEST.read_bytes())}))
        def commit(r=receipt, v=consumed):
            t.write(rp,i.json_bytes(r),0o600,1000,1000);t.write(cp,i.json_bytes(v),0o600,1000,1000)
        commit()
        return f, receipt, consumed, commit, (capability_id,transaction_id,bootstrap), rp

    def test_parent_accepts_precise_derived_receipt(self):
        f,r,v,commit,args,rp = self.receipt_fixture()
        self.assertEqual(c.validate_launcher_receipt(*args),c.sha(rp.read_bytes()))

    def test_parent_rejects_old_missing_or_false_derived_provenance(self):
        f,r,v,commit,args,rp = self.receipt_fixture()
        variants=[]
        x=copy.deepcopy(r);x['loaded_sources']['m9_openmx_build']['sha256']=c.DRIVER_BASE_SHA;variants.append(x)
        x=copy.deepcopy(r);x['loaded_sources']['m9_openmx_build'].pop('base_sha256');variants.append(x)
        x=copy.deepcopy(r);x['loaded_sources']['m9_openmx_build']['base_sha256']='0'*64;variants.append(x)
        x=copy.deepcopy(r);x['loaded_sources']['m9_openmx_build']['bytecode_consulted']=True;variants.append(x)
        x=copy.deepcopy(r);x['loaded_sources']['extra']={};variants.append(x)
        x=copy.deepcopy(r);x.pop('v4_binding');variants.append(x)
        x=copy.deepcopy(r);x['v4_binding']['operation_id']='a237ec1f2b404d898840c643e9ae501b';variants.append(x)
        for x in variants:
            with self.subTest(receipt=x):
                commit(x,v)
                with self.assertRaises(ValueError): c.validate_launcher_receipt(*args)

    def test_parent_rejects_action_parent_child_and_dependency_drift(self):
        f,r,v,commit,args,rp = self.receipt_fixture()
        for field,value in [('action','smoke_run'),('budget_argv',[]),('launcher_argv',[]),('forecast_bytes',0),
                            ('structure_id','500'),('state','BOUND'),('capability_id','3'*32)]:
            with self.subTest(field=field):
                x=copy.deepcopy(v);x[field]=value;commit(r,x)
                with self.assertRaises(ValueError):c.validate_launcher_receipt(*args)
        for field in ['pth_processed','site_addsitedir_called']:
            x=copy.deepcopy(r);x['dependency_path'][field]=True;commit(x,v)
            with self.assertRaises(ValueError):c.validate_launcher_receipt(*args)

    def test_static_authority_checks_actual_snapshot_and_install_fact(self):
        f=self.fixture();before=f.reader.capture_tree(c.ROOT)
        self.assertEqual(c.execution_binding()['operation_id'],c.OPERATION)
        self.assertEqual(before,f.reader.capture_tree(c.ROOT))
        t.write(c.INSTALL_REPORT,b'changed independent fact\n')
        with self.assertRaises(SystemExit):c.execution_binding()

    def test_real_budget_postchild_authority_drift_commits_failure_and_cpu(self):
        f=self.fixture()
        b=c.load_bytes('v4_budget_postchild',c.OLD_BUDGET,c.derive_budget(t.BASE))
        b.LOCK_PATH=c.LOCK;b.STATE_PATH=c.ROOT/'manifests/budget_state.json'
        b.OVERLAP_WORKFLOW_STATE=c.ROOT/'manifests/overlap_workflow_state.json'
        b.OVERLAP_TRANSACTION=c.ROOT/'manifests/overlap_transaction.json'
        b.LEDGER_PATH=c.ROOT/'manifests/budget_ledger.jsonl'
        b.OVERLAP_CAPABILITY_ROOT=c.ROOT/'manifests/overlap_capabilities'
        b.OVERLAP_CAPABILITY_ROOT.mkdir();b.LINUX_ROOT=c.ROOT
        state=json.loads(b.STATE_PATH.read_bytes())
        state.update(cpu_seconds={'overlap_build':14.0,'overlap_smoke':0.0,'overlap_batch':0.0},
                     gpu_seconds={'compatibility':54.0,'training':0.0,'physical_validation':0.0},
                     overlap_storage_baseline={})
        t.jwrite(b.STATE_PATH,state)
        prefix=b.LEDGER_PATH.read_bytes()
        os.chown(b.LEDGER_PATH,1000,1000);os.chmod(b.LEDGER_PATH,0o644)
        class Child:
            pid=999999
            def wait(self,timeout):
                # The sole independent variable is a post-child static authority change.
                t.write(c.INSTALL_REPORT,b'authority drift after child completion\n')
                return 0
        args=b.build_parser().parse_args(c.require_argv(c.RUN_ARGV))
        with mock.patch.object(c,'verify_gate',return_value=f.gate), \
             mock.patch.object(b.os,'geteuid',return_value=1000), \
             mock.patch.object(b,'isolated_bootstrap_provenance',return_value={}), \
             mock.patch.object(b,'wall_clock_policy_mode',return_value='UNLIMITED'), \
             mock.patch.object(b,'deadline_remaining',return_value=None), \
             mock.patch.object(b,'violations',return_value=[]), \
             mock.patch.object(b,'overlap_status_payload',return_value={}), \
             mock.patch.object(b,'storage_snapshot',return_value={}), \
             mock.patch.object(b.time,'monotonic_ns',side_effect=[1000000000,3000000000]), \
             mock.patch.object(b.subprocess,'Popen',return_value=Child()) as popen:
            c.guard_budget(b)
            result=b.command_overlap_run(args)
            self.assertEqual(result,125);popen.assert_called_once()
        after=json.loads(b.STATE_PATH.read_bytes());workflow=json.loads(b.OVERLAP_WORKFLOW_STATE.read_bytes())
        tx=json.loads(b.OVERLAP_TRANSACTION.read_bytes())
        self.assertTrue(after['hard_stopped']);self.assertTrue(workflow['hard_stopped'])
        self.assertEqual(after['cpu_seconds']['overlap_build'],16.0)
        self.assertEqual(after['gpu_seconds'],state['gpu_seconds'])
        self.assertIsNone(after['active_overlap_transaction']);self.assertIsNone(workflow['active_transaction'])
        self.assertEqual(tx['state'],'FAILED_COMMITTED');self.assertEqual(tx['elapsed_seconds'],2.0)
        self.assertTrue(any(x.startswith('launcher_receipt_invalid:ValueError:') for x in tx['reasons']))
        ledger=b.LEDGER_PATH.read_bytes();self.assertTrue(ledger.startswith(prefix))
        events=ledger[len(prefix):].splitlines();self.assertEqual(len(events),1)
        self.assertEqual(json.loads(events[0])['event'],'OVERLAP_HARD_STOP')


if __name__ == '__main__':
    unittest.main()
