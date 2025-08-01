#!/usr/bin/env python3
"""
Service Status Monitor
Monitora o status das APIs e gerencia fallbacks
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class ServiceStatus:
    """Status de um serviço"""
    name: str
    available: bool
    last_check: datetime
    error_count: int
    success_rate: float
    avg_response_time: float
    last_error: Optional[str] = None
    config_valid: bool = False

@dataclass
class SystemStatus:
    """Status geral do sistema"""
    overall_status: str
    services: Dict[str, ServiceStatus]
    last_updated: datetime
    recommendations: List[str]

class ServiceMonitor:
    """Monitor de serviços"""
    
    def __init__(self):
        self.services = {}
        self.status_file = 'data/service_status.json'
        self._load_status()
    
    def _load_status(self):
        """Carrega status salvo"""
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r') as f:
                    data = json.load(f)
                    for service_name, service_data in data.get('services', {}).items():
                        service_data['last_check'] = datetime.fromisoformat(service_data['last_check'])
                        self.services[service_name] = ServiceStatus(**service_data)
        except Exception as e:
            logger.warning(f"Erro ao carregar status: {e}")
    
    def _save_status(self):
        """Salva status atual"""
        try:
            os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
            data = {
                'last_updated': datetime.now().isoformat(),
                'services': {
                    name: asdict(service) for name, service in self.services.items()
                }
            }
            with open(self.status_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Erro ao salvar status: {e}")
    
    def check_groq_status(self) -> ServiceStatus:
        """Verifica status do Groq"""
        try:
            from llm.llm_client import ModularLLMClient
            import asyncio
            
            start_time = time.time()
            
            async def test_groq():
                client = ModularLLMClient(['Groq'])
                response = await client.generate("Teste de conectividade", max_tokens=5)
                return response.success
            
            success = asyncio.run(test_groq())
            response_time = time.time() - start_time
            
            # Atualizar ou criar status
            if 'groq' not in self.services:
                self.services['groq'] = ServiceStatus(
                    name='Groq',
                    available=False,
                    last_check=datetime.now(),
                    error_count=0,
                    success_rate=0.0,
                    avg_response_time=0.0
                )
            
            service = self.services['groq']
            service.last_check = datetime.now()
            
            if success:
                service.available = True
                service.error_count = max(0, service.error_count - 1)
                service.avg_response_time = (service.avg_response_time + response_time) / 2
                service.last_error = None
            else:
                service.available = False
                service.error_count += 1
                service.last_error = "Falha na geração de resposta"
            
            # Calcular taxa de sucesso
            service.success_rate = max(0.0, 1.0 - (service.error_count / 10))
            
            return service
            
        except Exception as e:
            logger.error(f"Erro ao verificar Groq: {e}")
            return ServiceStatus(
                name='Groq',
                available=False,
                last_check=datetime.now(),
                error_count=1,
                success_rate=0.0,
                avg_response_time=0.0,
                last_error=str(e)
            )
    
    def check_sendgrid_status(self) -> ServiceStatus:
        """Verifica status do SendGrid"""
        try:
            from email_sender.sendgrid_sender import SendGridSender
            
            start_time = time.time()
            sender = SendGridSender()
            success = sender.test_connection()
            response_time = time.time() - start_time
            
            # Atualizar ou criar status
            if 'sendgrid' not in self.services:
                self.services['sendgrid'] = ServiceStatus(
                    name='SendGrid',
                    available=False,
                    last_check=datetime.now(),
                    error_count=0,
                    success_rate=0.0,
                    avg_response_time=0.0
                )
            
            service = self.services['sendgrid']
            service.last_check = datetime.now()
            
            if success:
                service.available = True
                service.error_count = max(0, service.error_count - 1)
                service.avg_response_time = (service.avg_response_time + response_time) / 2
                service.last_error = None
            else:
                service.available = False
                service.error_count += 1
                service.last_error = "Erro 403 - Chave possivelmente expirada"
            
            # Calcular taxa de sucesso
            service.success_rate = max(0.0, 1.0 - (service.error_count / 10))
            
            return service
            
        except Exception as e:
            logger.error(f"Erro ao verificar SendGrid: {e}")
            return ServiceStatus(
                name='SendGrid',
                available=False,
                last_check=datetime.now(),
                error_count=1,
                success_rate=0.0,
                avg_response_time=0.0,
                last_error=str(e)
            )
    
    def check_all_services(self) -> SystemStatus:
        """Verifica status de todos os serviços"""
        logger.info("Verificando status de todos os serviços...")
        
        # Verificar Groq
        groq_status = self.check_groq_status()
        self.services['groq'] = groq_status
        
        # Verificar SendGrid
        sendgrid_status = self.check_sendgrid_status()
        self.services['sendgrid'] = sendgrid_status
        
        # Salvar status
        self._save_status()
        
        # Determinar status geral
        available_services = sum(1 for service in self.services.values() if service.available)
        total_services = len(self.services)
        
        if available_services == total_services:
            overall_status = "✅ OPERACIONAL"
        elif available_services > 0:
            overall_status = "⚠️ PARCIALMENTE OPERACIONAL"
        else:
            overall_status = "❌ CRÍTICO"
        
        # Gerar recomendações
        recommendations = self._generate_recommendations()
        
        return SystemStatus(
            overall_status=overall_status,
            services=self.services.copy(),
            last_updated=datetime.now(),
            recommendations=recommendations
        )
    
    def _generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas no status"""
        recommendations = []
        
        for service_name, service in self.services.items():
            if not service.available:
                if service_name == 'groq':
                    recommendations.append("🔑 Groq: Verificar GROQ_API_KEY no arquivo .env")
                elif service_name == 'sendgrid':
                    recommendations.append("🔑 SendGrid: Gerar nova chave API (erro 403 detectado)")
                    recommendations.append("📧 SendGrid: Verificar FROM_EMAIL e FROM_NAME")
            
            if service.error_count > 5:
                recommendations.append(f"⚠️ {service_name}: Muitos erros consecutivos - verificar configuração")
        
        if not recommendations:
            recommendations.append("✅ Todos os serviços funcionando normalmente")
        
        return recommendations
    
    def get_service_status(self, service_name: str) -> Optional[ServiceStatus]:
        """Obtém status de um serviço específico"""
        return self.services.get(service_name)
    
    def is_service_available(self, service_name: str) -> bool:
        """Verifica se um serviço está disponível"""
        service = self.services.get(service_name)
        return service.available if service else False
    
    def get_fallback_status(self) -> Dict:
        """Obtém status dos fallbacks"""
        return {
            'groq_fallback': not self.is_service_available('groq'),
            'sendgrid_fallback': not self.is_service_available('sendgrid'),
            'system_operational': any(service.available for service in self.services.values())
        }
    
    def print_status_report(self):
        """Imprime relatório de status"""
        status = self.check_all_services()
        
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO DE STATUS DOS SERVIÇOS")
        print("=" * 60)
        
        print(f"\n🎯 STATUS GERAL: {status.overall_status}")
        print(f"🕒 Última atualização: {status.last_updated.strftime('%d/%m/%Y %H:%M:%S')}")
        
        print("\n📋 SERVIÇOS:")
        for service_name, service in status.services.items():
            status_icon = "✅" if service.available else "❌"
            print(f"   {status_icon} {service.name}:")
            print(f"      Status: {'Disponível' if service.available else 'Indisponível'}")
            print(f"      Última verificação: {service.last_check.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"      Taxa de sucesso: {service.success_rate:.1%}")
            print(f"      Tempo médio: {service.avg_response_time:.2f}s")
            if service.last_error:
                print(f"      Último erro: {service.last_error}")
            print()
        
        print("💡 RECOMENDAÇÕES:")
        for i, recommendation in enumerate(status.recommendations, 1):
            print(f"   {i}. {recommendation}")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        if status.overall_status == "✅ OPERACIONAL":
            print("   • Sistema pronto para produção")
            print("   • Executar campanha de teste")
        elif status.overall_status == "⚠️ PARCIALMENTE OPERACIONAL":
            print("   • Corrigir serviços com problemas")
            print("   • Sistema funciona com limitações")
        else:
            print("   • Corrigir configurações das APIs")
            print("   • Verificar arquivo .env")
        
        print("=" * 60)

def main():
    """Função principal"""
    monitor = ServiceMonitor()
    monitor.print_status_report()

if __name__ == "__main__":
    main() 