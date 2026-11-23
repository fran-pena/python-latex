import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from pylatexenc.latexwalker import LatexWalker

from compylatex import compylatex
from compylatex.converter import tex_to_python_with_alias
from compylatex.executor import crear_funcion
from compylatex.parser import parse_env_node


EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def parse_algorithm(body, label="alg:calc:funcion", aliases=None):
    latex = (
        r"\begin{algorithm}\label{" + label + r"}"
        r"\begin{algorithmic}" + body
        + r"\end{algorithmic}\end{algorithm}"
    )
    nodes, _, _ = LatexWalker(latex).get_latex_nodes()
    namespace = {"__latex_alias__": aliases or {}}
    return parse_env_node(nodes[0], namespace)


class RequireTests(unittest.TestCase):
    def test_secant_example_uses_two_functions_and_preserves_require(self):
        source = EXAMPLES / "secante_require.tex"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "resultado.tex"
            with contextlib.redirect_stdout(io.StringIO()):
                compylatex(str(source), str(output))
            result = output.read_text(encoding="utf-8")
        self.assertIn(r"\REQUIRE $F, a, b, tol, limite$", result)
        self.assertIn("1.414214", result)
        self.assertIn("1.259921", result)

    def test_multiple_require_declarations_and_expressions(self):
        algorithm = parse_algorithm(
            r"\REQUIRE $F$, $a$"
            r"\REQUIRE $b$"
            r"\STATE $a = a + b$"
            r"\STATE $resultado = F(a)$"
            r"\RETURN $resultado$",
            aliases={"a": "global_a"},
        )
        self.assertEqual(algorithm["parameters"], ["F", "a", "b"])
        self.assertEqual(crear_funcion(algorithm)(lambda x: x + 1, 2, 3), 6)

    def test_calls_are_isolated_and_arguments_can_be_callables(self):
        algorithm = parse_algorithm(
            r"\REQUIRE $F$, $a$, $b$"
            r"\STATE $a = a + b$"
            r"\STATE $resultado = F(a)$"
            r"\RETURN $resultado$",
            aliases={"a": "global_a", "resultado": "global_resultado"},
        )
        function = crear_funcion(algorithm)
        self.assertEqual(function(lambda x: x * 2, 1, 2), 6)
        self.assertEqual(function(lambda x: x * 3, 5, 2), 21)
        with self.assertRaisesRegex(TypeError, "requiere 3 argumentos"):
            function(lambda x: x, 1)

    def test_explicit_definition_supports_subscripts_and_nested_return(self):
        algorithm = parse_algorithm(
            r"\REQUIRE $X_0$, $tol_{NR}$"
            r"\IF{$X_0 > tol_{NR}$}"
            r"\RETURN $X_0$"
            r"\ENDIF"
            r"\RETURN $tol_{NR}$",
            label="alg:def:seleccionar",
        )
        function = crear_funcion(algorithm)
        self.assertEqual(function(5, 3), 5)
        self.assertEqual(function(1, 3), 3)

    def test_invalid_declarations_fail_explicitly(self):
        for body in (
            r"\REQUIRE $a$, $a$\RETURN $a$",
            r"\REQUIRE texto explicativo\RETURN $a$",
            r"\REQUIRE $a$\RETURN $a$, $b$",
            r"\REQUIRE $a$\RETURN $a + 1$",
            r"\REQUIRE $a$\STATE $b = a$",
        ):
            with self.subTest(body=body):
                with self.assertRaises(ValueError):
                    parse_algorithm(body)
        with self.assertRaisesRegex(ValueError, "REQUIRE"):
            parse_algorithm(r"\RETURN $a$", label="alg:def:sinentradas")

    def test_no_return_on_executed_path_is_an_error(self):
        algorithm = parse_algorithm(
            r"\REQUIRE $a$"
            r"\IF{$a > 0$}\RETURN $a$\ENDIF"
        )
        with self.assertRaisesRegex(ValueError, "sin ejecutar"):
            crear_funcion(algorithm)(-1)

    def test_algorithm_without_require_retains_immediate_execution(self):
        source = (
            r"\begin{equation}a = 3\label{eq:calc:a}\end{equation}"
            r"\begin{algorithm}\label{alg:calc:b}\begin{algorithmic}"
            r"\ENSURE $b$\STATE $b = a + 1$\RETURN $b$"
            r"\end{algorithmic}\end{algorithm}"
            r"\begin{equation}b = \label{eq:res:b}\end{equation}"
        )
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "original.tex"
            output_path = Path(directory) / "resultado.tex"
            input_path.write_text(source, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                compylatex(str(input_path), str(output_path))
            result = output_path.read_text(encoding="utf-8")
        self.assertIn("b = 4", result)
        self.assertIn(r"\ENSURE $b$", result)

    def test_function_call_respects_global_aliases_without_mutating_them(self):
        source = (
            r"\begin{equation}a = 10\label{eq:calc:aa}\end{equation}"
            r"\begin{algorithm}\label{alg:calc:calcula}\begin{algorithmic}"
            r"\REQUIRE $a$\ENSURE $a$"
            r"\STATE $a = a + 1$\RETURN $a$"
            r"\end{algorithmic}\end{algorithm}"
            r"\begin{equation}r = calcula(a)\label{eq:calc:r}\end{equation}"
            r"\begin{equation}r = \label{eq:res:r}\end{equation}"
            r"\begin{equation}a = \label{eq:res:aa}\end{equation}"
        )
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "original.tex"
            output_path = Path(directory) / "resultado.tex"
            input_path.write_text(source, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                compylatex(str(input_path), str(output_path))
            result = output_path.read_text(encoding="utf-8")
        self.assertIn("r = 11", result)
        self.assertIn("a = 10", result)
        self.assertIn(r"\ENSURE $a$", result)

    def test_function_call_replaces_aliases_only_once(self):
        namespace = {
            "__latex_alias__": {"a": "b", "b": "c"},
            "__algorithm_functions__": {"calcula"},
        }
        self.assertEqual(
            tex_to_python_with_alias("calcula(a, b)", namespace),
            "calcula(b, c)",
        )


if __name__ == "__main__":
    unittest.main()
