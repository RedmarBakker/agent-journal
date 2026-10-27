import ast
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "journal"
LEAST_FUNCTIONS = 3
LEAST_FILES = 2
SAME_QUESTION = {"Eq": "==", "NotEq": "==", "Is": "is", "IsNot": "is", "In": "in", "NotIn": "in"}


@dataclass
class Question:
    """One comparison of a field with a value, asked by its sites, the functions that ask it; == and != are one question, as are is and is not."""

    field_name: str
    operator: str
    value: str
    sites: set[tuple[str, str]] = field(default_factory=set)

    def files(self) -> set[str]:
        return {path for path, _ in self.sites}

    def is_repeated(self) -> bool:
        return len(self.sites) >= LEAST_FUNCTIONS and len(self.files()) >= LEAST_FILES

    def text(self) -> str:
        return f"{self.field_name} {self.operator} {self.value}"


class RepeatedFieldChecks:
    """Finds a missing funnel: one field of the project's own data classes compared with the same value, the same way, in three or more functions across two or more files, and the method on the field's class that already asks it, when one does."""

    def __init__(self, source: Path) -> None:
        self.source = source
        self.trees = {path: ast.parse(path.read_text()) for path in sorted(source.rglob("*.py")) if "__pycache__" not in path.parts}
        self.fields = self.data_fields()
        self.named = self.named_questions()

    def data_fields(self) -> set[str]:
        return {target.id for tree in self.trees.values() for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and self.is_dataclass(node)
                for statement in node.body if isinstance(statement, ast.AnnAssign) and isinstance(target := statement.target, ast.Name)}

    @staticmethod
    def is_dataclass(node: ast.ClassDef) -> bool:
        return any("dataclass" in ast.unparse(decorator) for decorator in node.decorator_list)

    def named_questions(self) -> dict[tuple[str, str, str], str]:
        named = {}
        for path, tree in self.trees.items():
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                for method in node.body:
                    question = self.method_question(method)
                    if question:
                        named[question] = f"{node.name}.{method.name}"
        return named

    def method_question(self, method: ast.stmt) -> tuple[str, str, str] | None:
        if not isinstance(method, ast.FunctionDef) or len(method.body) != 1 or not isinstance(method.body[0], ast.Return):
            return None
        returned = method.body[0].value
        return self.question_key(returned) if isinstance(returned, ast.Compare) else None

    def question_key(self, node: ast.Compare) -> tuple[str, str, str] | None:
        if len(node.ops) != 1 or not isinstance(node.left, ast.Attribute) or node.left.attr not in self.fields:
            return None
        value = node.comparators[0]
        if not isinstance(value, (ast.Constant, ast.Attribute)):
            return None
        return node.left.attr, SAME_QUESTION.get(type(node.ops[0]).__name__, ""), ast.unparse(value)

    def questions(self) -> list[Question]:
        found: dict[tuple[str, str, str], Question] = {}
        for path, tree in self.trees.items():
            for function in ast.walk(tree):
                if isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)) and self.method_question(function) is None:
                    self.collect(found, function, str(path.relative_to(self.source.parent.parent)))
        return sorted((question for question in found.values() if question.is_repeated()), key=lambda question: -len(question.sites))

    def collect(self, found: dict[tuple[str, str, str], Question], function: ast.AST, path: str) -> None:
        for node in ast.walk(function):
            key = self.question_key(node) if isinstance(node, ast.Compare) else None
            if key and key[1]:
                found.setdefault(key, Question(*key)).sites.add((path, getattr(function, "name", "")))

    def lines(self) -> list[str]:
        rows = []
        for question in self.questions():
            method = self.named.get((question.field_name, question.operator, question.value))
            advice = f"use {method}, which asks it already" if method else "name it once, as a method on the class that holds the field"
            rows.append(f"{question.text()}: {len(question.sites)} functions in {len(question.files())} files; {advice}")
            rows.extend(f"    {path} {name}" for path, name in sorted(question.sites))
        return rows


if __name__ == "__main__":
    found = RepeatedFieldChecks(SOURCE).lines()
    print("\n".join(found) if found else "no field is compared the same way in many places")
    sys.exit(1 if found else 0)
