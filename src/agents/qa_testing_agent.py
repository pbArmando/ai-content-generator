"""
QATestingAgent - Agente de testing y control de calidad
Ejecuta tests automatizados y reporta resultados
"""

import os
import sys
import subprocess
import json
import unittest
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import re

# Fix UTF-8 para Windows
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


@dataclass
class TestResult:
    """Resultado de un test"""
    test_name: str
    status: str  # pass, fail, error, skip
    duration: float
    message: str = ""
    error_trace: str = ""


@dataclass
class TestSuiteReport:
    """Reporte de suite de tests"""
    timestamp: str
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    duration: float = 0.0
    results: List[TestResult] = field(default_factory=list)
    coverage: float = 0.0
    overall_status: str = "unknown"  # pass, fail, error


class QATestingAgent:
    """
    Agente de QA para testing automatizado.
    Ejecuta tests y reporta resultados.
    """
    
    # Test patterns para diferentes tipos de código
    TEST_PATTERNS = {
        'python': {
            'test_dir': 'tests',
            'test_file_pattern': 'test_*.py',
            'run_command': 'python -m pytest {test_path} -v --tb=short',
            'coverage_command': 'python -m pytest --cov={module} --cov-report=term-missing'
        },
        'javascript': {
            'test_dir': 'frontend/src/__tests__',
            'test_file_pattern': '*.test.js',
            'run_command': 'npm test -- --passWithNoTests',
            'coverage_command': 'npm test -- --coverage'
        },
        'api': {
            'test_dir': 'tests/api',
            'test_file_pattern': 'test_api*.py',
            'run_command': 'pytest {test_path} -v'
        }
    }
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.test_results = []
        self.test_history = []
        
    def discover_tests(self) -> List[str]:
        """Descubre todos los tests disponibles"""
        tests = []
        
        # Buscar tests de Python
        for pattern in ['test_*.py', '*_test.py']:
            for test_file in self.project_root.rglob(pattern):
                if 'venv' not in str(test_file) and '__pycache__' not in str(test_file):
                    tests.append(str(test_file))
        
        # Buscar tests de JavaScript
        for pattern in ['*.test.js', '*.spec.js']:
            test_dir = self.project_root / 'frontend' / 'src' / '__tests__'
            if test_dir.exists():
                for test_file in test_dir.glob(pattern):
                    tests.append(str(test_file))
        
        return tests
    
    def run_test_suite(self, test_path: str = None, test_type: str = 'python') -> TestSuiteReport:
        """Ejecuta una suite de tests"""
        report = TestSuiteReport(
            timestamp=datetime.now().isoformat()
        )
        
        print("\n" + "="*60)
        print("🧪 INICIANDO SUITE DE TESTS")
        print("="*60)
        
        if test_path:
            # Ejecutar test específico
            return self._run_single_test(test_path, test_type)
        
        # Ejecutar todos los tests
        tests = self.discover_tests()
        
        if not tests:
            print("  ⚠️ No se encontraron tests")
            report.overall_status = "skip"
            return report
        
        print(f"  📋 Tests encontrados: {len(tests)}")
        
        # Ejecutar cada test
        for test_file in tests:
            try:
                result = self._run_single_test(test_file, test_type)
                report.results.extend(result.results)
                report.total_tests += result.total_tests
                report.passed += result.passed
                report.failed += result.failed
                report.errors += result.errors
                report.duration += result.duration
            except Exception as e:
                print(f"  ❌ Error ejecutando {test_file}: {e}")
                report.errors += 1
        
        # Calcular estado final
        if report.failed > 0 or report.errors > 0:
            report.overall_status = "fail"
        elif report.passed > 0:
            report.overall_status = "pass"
        else:
            report.overall_status = "skip"
        
        return report
    
    def _run_single_test(self, test_path: str, test_type: str = 'python') -> TestSuiteReport:
        """Ejecuta un test individual"""
        report = TestSuiteReport(
            timestamp=datetime.now().isoformat()
        )
        
        test_file = Path(test_path)
        
        if test_type == 'python' and test_file.suffix == '.py':
            try:
                # Usar pytest si está disponible
                result = subprocess.run(
                    ['python', '-m', 'pytest', str(test_file), '-v', '--tb=short', '--json-report', '--json-report-file=test_report.json'],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=self.project_root
                )
                
                # Parsear output
                output = result.stdout + result.stderr
                report = self._parse_pytest_output(output, test_file.name)
                
            except FileNotFoundError:
                # pytest no disponible, usar unittest
                result = subprocess.run(
                    ['python', '-m', 'unittest', str(test_file), '-v'],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=self.project_root
                )
                output = result.stdout + result.stderr
                report = self._parse_unittest_output(output, test_file.name)
                
            except subprocess.TimeoutExpired:
                report.results.append(TestResult(
                    test_name=test_file.name,
                    status='error',
                    duration=60,
                    message='Test timeout'
                ))
                report.errors = 1
                report.overall_status = "error"
                
            except Exception as e:
                report.results.append(TestResult(
                    test_name=test_file.name,
                    status='error',
                    duration=0,
                    message=str(e)
                ))
                report.errors = 1
                report.overall_status = "error"
        
        elif test_type == 'javascript':
            try:
                result = subprocess.run(
                    ['npm', 'test', '--', '--watchAll=false', '--json'],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=self.project_root / 'frontend'
                )
                output = result.stdout + result.stderr
                report = self._parse_jest_output(output, test_file.name)
            except Exception as e:
                report.results.append(TestResult(
                    test_name=test_file.name,
                    status='error',
                    duration=0,
                    message=str(e)
                ))
                report.errors = 1
        
        return report
    
    def _parse_pytest_output(self, output: str, test_name: str) -> TestSuiteReport:
        """Parsea output de pytest"""
        report = TestSuiteReport(timestamp=datetime.now().isoformat())
        
        # Contar resultados
        passed = len(re.findall(r'PASSED', output))
        failed = len(re.findall(r'FAILED', output))
        errors = len(re.findall(r'ERROR', output))
        
        # Buscar duración
        duration_match = re.search(r'(\d+\.?\d*)s', output)
        if duration_match:
            report.duration = float(duration_match.group(1))
        
        # Extraer detalles de cada test
        for line in output.split('\n'):
            if 'PASSED' in line or 'FAILED' in line or 'ERROR' in line:
                parts = line.split()
                if parts:
                    name = parts[0] if len(parts) > 0 else test_name
                    status = 'pass' if 'PASSED' in line else ('fail' if 'FAILED' in line else 'error')
                    report.results.append(TestResult(
                        test_name=name,
                        status=status,
                        duration=report.duration / max(passed + failed, 1),
                        message=line.strip()
                    ))
        
        report.total_tests = passed + failed + errors
        report.passed = passed
        report.failed = failed
        report.errors = errors
        report.overall_status = 'fail' if failed > 0 or errors > 0 else 'pass'
        
        return report
    
    def _parse_unittest_output(self, output: str, test_name: str) -> TestSuiteReport:
        """Parsea output de unittest"""
        report = TestSuiteReport(timestamp=datetime.now().isoformat())
        
        # Buscar estadísticas
        stats_match = re.search(r'Ran (\d+) test', output)
        if stats_match:
            report.total_tests = int(stats_match.group(1))
        
        # Buscar OK o FAILED
        if 'OK' in output:
            report.passed = report.total_tests
            report.overall_status = 'pass'
        elif 'FAILED' in output:
            report.overall_status = 'fail'
            # Contar fails
            report.failed = output.count('FAIL:')
        
        return report
    
    def _parse_jest_output(self, output: str, test_name: str) -> TestSuiteReport:
        """Parsea output de Jest"""
        report = TestSuiteReport(timestamp=datetime.now().isoformat())
        
        # Intentar parsear JSON
        try:
            json_match = re.search(r'\{.*"numPassedTests".*\}', output)
            if json_match:
                data = json.loads(json_match.group())
                report.passed = data.get('numPassedTests', 0)
                report.failed = data.get('numFailedTests', 0)
                report.total_tests = report.passed + report.failed
                report.duration = data.get('displayDuration', 0) / 1000
        except:
            pass
        
        report.overall_status = 'fail' if report.failed > 0 else 'pass'
        
        return report
    
    def run_integration_tests(self) -> TestSuiteReport:
        """Ejecuta tests de integración del sistema"""
        print("\n" + "="*60)
        print("🔗 EJECUTANDO TESTS DE INTEGRACIÓN")
        print("="*60)
        
        report = TestSuiteReport(timestamp=datetime.now().isoformat())
        
        # Test 1: Verificar que backend responde
        report.results.append(self._test_backend_health())
        
        # Test 2: Verificar que API genera artículo
        report.results.append(self._test_generate_article())
        
        # Test 3: Verificar que PromptAgent funciona
        report.results.append(self._test_prompt_agent())
        
        # Test 4: Verificar que SocialMediaAgent funciona
        report.results.append(self._test_social_media_agent())
        
        # Calcular resultados
        report.total_tests = len(report.results)
        report.passed = sum(1 for r in report.results if r.status == 'pass')
        report.failed = sum(1 for r in report.results if r.status == 'fail')
        report.errors = sum(1 for r in report.results if r.status == 'error')
        report.overall_status = 'fail' if report.failed > 0 or report.errors > 0 else 'pass'
        
        return report
    
    def _test_backend_health(self) -> TestResult:
        """Test: Backend está corriendo"""
        import socket
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 8000))
            sock.close()
            
            if result == 0:
                return TestResult(
                    test_name='backend_health',
                    status='pass',
                    duration=0.1,
                    message='Backend respondiendo en puerto 8000'
                )
            else:
                return TestResult(
                    test_name='backend_health',
                    status='skip',
                    duration=0.1,
                    message='Backend no está corriendo (iniciar con python backend/main.py)'
                )
        except Exception as e:
            return TestResult(
                test_name='backend_health',
                status='error',
                duration=0.1,
                message=str(e)
            )
    
    def _test_generate_article(self) -> TestResult:
        """Test: Generador de artículos funciona"""
        sys.path.insert(0, str(self.project_root / 'src'))
        
        try:
            from agents.orchestrator import OrchestratorAgent
            
            orchestrator = OrchestratorAgent()
            article = orchestrator.generate_article(
                topic="test topic",
                tone="profesional",
                research_context=""
            )
            
            if article and 'title' in article and 'introduction' in article:
                return TestResult(
                    test_name='generate_article',
                    status='pass',
                    duration=1.0,
                    message='Artículo generado correctamente'
                )
            else:
                return TestResult(
                    test_name='generate_article',
                    status='fail',
                    duration=1.0,
                    message='Artículo generado pero sin contenido válido'
                )
        except Exception as e:
            return TestResult(
                test_name='generate_article',
                status='error',
                duration=1.0,
                message=str(e)
            )
    
    def _test_prompt_agent(self) -> TestResult:
        """Test: PromptAgent detecta tono correctamente"""
        sys.path.insert(0, str(self.project_root / 'src'))
        
        try:
            from agents.prompt_agent import PromptAgent
            
            agent = PromptAgent()
            
            # Test tema profesional de salud
            test_article = {
                'topic': 'detección temprana autismo neuropsicología',
                'title': 'Test',
                'tone': 'profesional',
                'introduction': 'La detección temprana del autismo es fundamental...',
                'conclusion': 'Conclusión del artículo.'
            }
            
            analysis = agent.analyze_article(test_article)
            
            if analysis['visual_tone'] in ['SALUD_BIENESTAR', 'SERIO_PROFESIONAL']:
                return TestResult(
                    test_name='prompt_agent_tone_detection',
                    status='pass',
                    duration=0.5,
                    message=f"Tono detectado correctamente: {analysis['visual_tone']}"
                )
            else:
                return TestResult(
                    test_name='prompt_agent_tone_detection',
                    status='fail',
                    duration=0.5,
                    message=f"Tono incorrecto: {analysis['visual_tone']}"
                )
        except Exception as e:
            return TestResult(
                test_name='prompt_agent_tone_detection',
                status='error',
                duration=0.5,
                message=str(e)
            )
    
    def _test_social_media_agent(self) -> TestResult:
        """Test: SocialMediaAgent genera posts"""
        sys.path.insert(0, str(self.project_root / 'src'))
        
        try:
            from agents.social_media_agent import SocialMediaAgent
            
            agent = SocialMediaAgent()
            
            test_article = {
                'title': 'Test Article',
                'topic': 'test topic',
                'introduction': 'Introduction',
                'conclusion': 'Conclusion',
                'sections': []
            }
            
            posts = agent.generate_all(test_article)
            
            if posts and len(posts) >= 4:
                return TestResult(
                    test_name='social_media_generation',
                    status='pass',
                    duration=1.0,
                    message=f"Posts generados para {len(posts)} plataformas"
                )
            else:
                return TestResult(
                    test_name='social_media_generation',
                    status='fail',
                    duration=1.0,
                    message="Posts no generados correctamente"
                )
        except Exception as e:
            return TestResult(
                test_name='social_media_generation',
                status='error',
                duration=1.0,
                message=str(e)
            )
    
    def generate_report(self, report: TestSuiteReport) -> str:
        """Genera reporte de tests"""
        output = []
        output.append("\n" + "="*60)
        output.append("📊 REPORTE DE TESTS - QA")
        output.append("="*60)
        output.append(f"Fecha: {report.timestamp}")
        output.append(f"Estado: {report.overall_status.upper()}")
        output.append(f"Tests: {report.passed}/{report.total_tests} passed")
        
        if report.failed > 0:
            output.append(f"❌ Failed: {report.failed}")
        if report.errors > 0:
            output.append(f"⚠️ Errors: {report.errors}")
        
        output.append(f"Duración: {report.duration:.2f}s")
        output.append("")
        
        # Detalle de resultados
        for result in report.results:
            if result.status == 'pass':
                icon = "✅"
            elif result.status == 'fail':
                icon = "❌"
            elif result.status == 'error':
                icon = "⚠️"
            else:
                icon = "⏭️"
            
            output.append(f"  {icon} {result.test_name}: {result.message}")
        
        return "\n".join(output)


def main():
    """Test del agente de QA"""
    import sys
    project_root = sys.argv[1] if len(sys.argv) > 1 else None
    
    agent = QATestingAgent(project_root)
    
    # Ejecutar tests de integración
    report = agent.run_integration_tests()
    
    print(agent.generate_report(report))
    
    # Guardar reporte
    report_file = 'outputs/qa_test_report.txt'
    os.makedirs('outputs', exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(agent.generate_report(report))
    
    print(f"\n📁 Reporte guardado en: {report_file}")


if __name__ == "__main__":
    main()
