from random import choice, randint
import undetected_chromedriver as uc
from time import sleep as sl
from datetime import datetime, timedelta

class Page:
  def __init__(self, headless:bool=False) -> None:
    self.driver:uc.Chrome = self.create_undetectable_driver(headless=headless)
  
  def create_undetectable_driver(self, headless:bool=False) -> uc.Chrome:
      """
      Cria um driver Chrome indetectável com suporte opcional ao modo headless
      
      Args:
          headless (bool): Se True, executa em modo headless
      """
      
      options = uc.ChromeOptions()
      # Configurações básicas de proteção
      options.add_argument('--disable-blink-features=AutomationControlled')
      options.add_argument('--disable-dev-shm-usage')
      options.add_argument('--no-sandbox')
      options.add_argument('--disable-gpu')
      
      # Proteção contra fingerprinting
      options.add_argument('--disable-webgl')
      options.add_argument('--disable-canvas-aa')
      options.add_argument('--disable-2d-canvas-clip-aa')
      options.add_argument('--disable-readings')
      
      # Configurações específicas para headless
      if headless:
          options.add_argument('--headless=new')  # Usa o novo modo headless do Chrome
          options.add_argument('--hide-scrollbars')
          options.add_argument('--mute-audio')
          
          # Adiciona argumentos extras para melhor compatibilidade em modo headless
          options.add_argument('--force-device-scale-factor=1')
          options.add_argument('--force-color-profile=srgb')
          options.add_argument('--disable-accelerated-2d-canvas')
          
      # Randomização de resolução de tela
      if headless:
          # No modo headless, define uma resolução mais comum
          options.add_argument('--window-size=1920,1080')
      else:
          window_width = randint(1200, 1300)
          window_height = randint(800, 900)
          options.add_argument(f'--window-size={window_width},{window_height}')
      
      # Configurações de localização e idioma
      options.add_argument('--lang=pt-BR,pt')
      options.add_argument('--timezone=America/Sao_Paulo')
      
      # User agents mais realistas
      user_agents = [
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
      ]
      options.add_argument(f'--user-agent={choice(user_agents)}')

      try:
          driver = uc.Chrome(options=options)
          
          # Scripts CDP aprimorados para modificar o fingerprinting do navegador
          driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
              "source": """
                  // Sobrescreve propriedades do navigator
                  Object.defineProperty(navigator, 'webdriver', {
                      get: () => undefined
                  });
                  
                  // Simula um ambiente gráfico mesmo em headless
                  if (navigator.userAgent.includes('HeadlessChrome')) {
                      Object.defineProperty(navigator, 'plugins', {
                          get: () => [
                              {
                                  0: {type: "application/x-google-chrome-pdf"},
                                  description: "Portable Document Format",
                                  filename: "internal-pdf-viewer",
                                  length: 1,
                                  name: "Chrome PDF Plugin"
                              }
                          ]
                      });
                      
                      Object.defineProperty(navigator, 'languages', {
                          get: () => ['pt-BR', 'pt', 'en-US', 'en']
                      });
                  }
                  
                  // Modifica permissões
                  const originalQuery = window.navigator.permissions.query;
                  window.navigator.permissions.query = (parameters) => (
                      parameters.name === 'notifications' ?
                          Promise.resolve({state: Notification.permission}) :
                          originalQuery(parameters)
                  );
                  
                  // Randomiza concorrência de hardware
                  Object.defineProperty(navigator, 'hardwareConcurrency', {
                      get: () => Math.floor(Math.random() * (8 - 4 + 1) + 4)
                  });
                  
                  // Adiciona ruído às medições de performance
                  const originalGetTiming = window.performance.timing.constructor.prototype.getEntriesByType;
                  window.performance.timing.constructor.prototype.getEntriesByType = function() {
                      const entries = originalGetTiming.apply(this, arguments);
                      if (entries.length && entries[0].duration) {
                          entries[0].duration += Math.random() * 10;
                      }
                      return entries;
                  };
                  
                  // Simula eventos de mouse mesmo em headless
                  if (navigator.userAgent.includes('HeadlessChrome')) {
                      const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
                      WebGLRenderingContext.prototype.getParameter = function(parameter) {
                          // Simula valores realistas de WebGL
                          if (parameter === 37445) {
                              return 'Intel Inc.';
                          }
                          if (parameter === 37446) {
                              return 'Intel(R) Iris(TM) Graphics 6100';
                          }
                          return originalGetParameter.call(this, parameter);
                      };
                  }
              """
          })
          
          return driver
          
      except Exception as e:
          print(f"Erro ao criar driver: {str(e)}")
          if 'driver' in locals():
              try:
                  driver.quit()
              except:
                  pass
          raise
      
  def espera_aparecer(self, element:str, segundos:int=10) -> None:
    limite = datetime.now() + timedelta(seconds=segundos)
    while True:
      if limite < datetime.now():
        raise Exception(f'Tempo limite excedido no elemento:\n{element}')
      try:
        self.driver.find_element('xpath', element)
        break
      except:
        sl(0.5)

  def preenche(self, text:str, element:str, tipo:str='xpath', index:int=0) -> None:
    self.espera_aparecer(element)
    if not index:
      try:
        self.driver.find_element(tipo, element).send_keys(text)
      except:
        sla = self.driver.find_elements(tipo, element)
        if len(sla) > 1:
          raise Exception(f"Encontrado {len(sla)} elementos:\n{element}")
    else:
      try:
        self.driver.find_elements(tipo, element)[index].send_keys(text)
      except:
        sla = self.driver.find_elements(tipo, element)
        if len(sla) == 1:
          raise Exception(f"elemento unico:\n{element}")
        
  def click(self, element:str, tipo:str='xpath', index:int=0) -> None:
    self.espera_aparecer(element)
    if not index:
      try:
        self.driver.find_element(tipo, element).click()
      except:
        sla = self.driver.find_elements(tipo, element)
        if len(sla) > 1:
          raise Exception(f"Encontrado {len(sla)} elementos:\n{element}")
    else:
      try:
        self.driver.find_elements(tipo, element)[index].click()
      except:
        sla = self.driver.find_elements(tipo, element)
        if len(sla) == 1:
          raise Exception(f"elemento unico:\n{element}")