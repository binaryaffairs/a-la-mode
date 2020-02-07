from bencode import bencode, bdecode, bread, bwrite
from dataclasses import dataclass, field
from toolz.dicttoolz import assoc, dissoc, merge
from toolz.itertoolz import first, drop
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
        self.tasks[name] = Task(name, spec)

    def encode(self):
        result = {
            "tasks": {name : encode(task) for name, task in self.tasks.items()},
            "meta": self.spec
        }
        return result

@dataclass
class Task:
    name: str
    spec: dict
    deps: list = field(default_factory=list)
    inputs: dict = field(default_factory=dict)

    def add_dep(self, other_task):
        self.deps.append(other_task)

def encode(task):
    if not task.deps:
        result = assoc(task.spec, 'inputs', task.inputs)
        output_sha = sha1(bencode(result))
        return assoc(result, 'output', output_sha)
    first_dep = task.deps[0]
    inputs = assoc(task.inputs, first_dep.name, encode(first_dep)['output'])
    return encode(Task(task.name, task.spec, task.deps[1:], inputs))

