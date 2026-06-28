"""
Propósito: recortar excessos inferiores que possam ter ficado nas imagens, usando a faixa como referência
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 28/06/2026

OBS1: puxe a pasta "questoes" do passo anterior para este passo 11
OBS2: atualizada a cor alvo para o RGB (35, 31, 32) conforme especificado.
OBS4: Padrão dinâmico adaptado: Faixa escura (4-5px) -> Faixa branca (4px) -> Faixa escura (4-5px).
"""
from PIL import Image
import os
import shutil

def encontrar_faixa_inferior(imagem, cor_alvo, tolerancia=15):
    """
    Encontra a faixa descrita de baixo para cima analisando o padrão dinâmico:
    - Faixa inferior: 4 a 5 pixels da cor_alvo
    - Faixa do meio: exatamente 4 pixels brancos (255, 255, 255)
    - Faixa superior: 4 a 5 pixels da cor_alvo
    
    Retorna a posição Y onde deve ser feito o corte (acima da faixa superior) ou None se não encontrar
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    x_central = largura // 2
    
    # Percorre a imagem de baixo para cima
    y = altura - 1
    while y >= 20:
        # 1. Verifica a Faixa Inferior (de baixo para cima, os primeiros pixels escuros)
        tamanho_faixa_inf = 0
        while y >= 0 and tamanho_faixa_inf < 6:
            pixel = pixels[x_central, y]
            r, g, b = pixel[:3]
            if (abs(r - cor_alvo[0]) <= tolerancia and 
                abs(g - cor_alvo[1]) <= tolerancia and 
                abs(b - cor_alvo[2]) <= tolerancia):
                tamanho_faixa_inf += 1
                y -= 1
            else:
                break
        
        # Se a faixa inferior não tem 4 ou 5 pixels, não é o nosso padrão
        if tamanho_faixa_inf not in (4, 5):
            if tamanho_faixa_inf > 0:
                continue 
            y -= 1
            continue

        # 2. Verifica a Faixa Branca do Meio (exatamente 4 pixels)
        tamanho_faixa_branca = 0
        while y >= 0 and tamanho_faixa_branca < 5:
            pixel = pixels[x_central, y]
            r, g, b = pixel[:3]
            if (abs(r - 255) <= tolerancia and 
                abs(g - 255) <= tolerancia and 
                abs(b - 255) <= tolerancia):
                tamanho_faixa_branca += 1
                y -= 1
            else:
                break

        # Se a faixa branca não tem exatamente 4 pixels, reinicia a busca
        if tamanho_faixa_branca != 4:
            continue

        # 3. Verifica a Faixa Superior (4 a 5 pixels escuros)
        tamanho_faixa_sup = 0
        while y >= 0 and tamanho_faixa_sup < 6:
            pixel = pixels[x_central, y]
            r, g, b = pixel[:3]
            if (abs(r - cor_alvo[0]) <= tolerancia and 
                abs(g - cor_alvo[1]) <= tolerancia and 
                abs(b - cor_alvo[2]) <= tolerancia):
                tamanho_faixa_sup += 1
                y -= 1
            else:
                break

        # Se a faixa superior também tem 4 ou 5 pixels, o padrão completo foi localizado!
        if tamanho_faixa_sup in (4, 5):
            posicao_corte = y + 1 
            print(f"Faixa encontrada! Padrão [{tamanho_faixa_inf}px escuro | {tamanho_faixa_branca}px branco | {tamanho_faixa_sup}px escuro]. Cortando em y={posicao_corte}")
            return posicao_corte

    return None

def processar_imagens(pasta_origem, pasta_destino, cor_alvo):
    """
    Processa todas as imagens da pasta origem, recortando as que têm a faixa padrão inferior
    e copiando todas para a pasta destino
    """
    os.makedirs(pasta_destino, exist_ok=True)
    
    arquivos = [f for f in os.listdir(pasta_origem) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
    
    print(f"Encontrados {len(arquivos)} arquivos para processar")
    
    for arquivo in arquivos:
        caminho_origem = os.path.join(pasta_origem, arquivo)
        caminho_destino = os.path.join(pasta_destino, arquivo)
        
        try:
            with Image.open(caminho_origem) as imagem:
                print(f"\nProcessando: {arquivo} ({imagem.width}x{imagem.height})")
                
                # CHAMADA CORRIGIDA AQUI: encontrar_faixa_inferior
                posicao_corte = encontrar_faixa_inferior(imagem, cor_alvo)
                
                if posicao_corte is not None and posicao_corte > 0:
                    area_corte = (0, 0, imagem.width, posicao_corte)
                    imagem_recortada = imagem.crop(area_corte)
                    imagem_recortada.save(caminho_destino)
                    print(f"✓ Imagem recortada: {imagem_recortada.width}x{imagem_recortada.height}")
                else:
                    shutil.copy2(caminho_origem, caminho_destino)
                    print(f"✓ Imagem mantida original (sem faixa detectada)")
                    
        except Exception as e:
            print(f"✗ Erro ao processar {arquivo}: {e}")
            try:
                shutil.copy2(caminho_origem, caminho_destino)
                print(f"✓ Arquivo copiado mesmo com erro")
            except:
                print(f"✗ Não foi possível copiar o arquivo")

if __name__ == "__main__":
    pasta_origem = "./questoes"
    pasta_destino = "finalizadas"
    cor_alvo = (35, 31, 32)  # Configurado para o seu padrão RGB (35,31,32)
    
    print("Iniciando processamento de imagens...")
    print(f"Pasta origem: {pasta_origem}")
    print(f"Pasta destino: {pasta_destino}")
    print(f"Cor alvo: RGB{cor_alvo}")
    
    if not os.path.exists(pasta_origem):
        print(f"Erro: A pasta '{pasta_origem}' não existe!")
        exit(1)
    
    processar_imagens(pasta_origem, pasta_destino, cor_alvo)
    
    print("\n" + "="*50)
    print("Processamento concluído!")
    print(f"Todas as imagens foram salvas em: {pasta_destino}")