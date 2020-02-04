from bencode import bencode, bdecode, bread, bwrite
from dataclasses import dataclass, field
from toolz.dicttoolz import assoc, dissoc
import pprint
pp = pprint.PrettyPrinter(indent=2).pprint
import hashlib

def sha1(s):
    return hashlib.sha1(s).hexdigest()

@dataclass
class Dag:
    spec: dict
    tasks: dict = field(default_factory=dict)

    def task(self, name, spec):
        self.tasks[name] = Task(assoc(spec, 'name', name))


@dataclass
class Task:
    spec: dict

    def __post_init__(self):
        self.refresh_output()

    def refresh_output(self):
        self.spec['output'] = sha1(bencode(dissoc(self.spec, 'output')))


    def add_dep(self, other_task):
        other_task.refresh_output()
        dep_name = other_task.spec['name']
        inputs = self.spec.get('inputs', {})
        self.spec['inputs'] = inputs
        self.spec['inputs'][dep_name] = other_task.spec['output']
        self.refresh_output()

def encode_dag(dag):
    return bencode([task.spec for task in dag])
