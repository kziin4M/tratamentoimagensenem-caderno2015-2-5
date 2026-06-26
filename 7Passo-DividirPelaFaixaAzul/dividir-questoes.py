from PIL import Image
import os

def converter_cor_gimp_para_rgb(gimp_r, gimp_g, gimp_b):
    """
    Converte valores do GIMP (0-100) para RGB (0-255)
    """
    r = int((gimp_r / 100) * 255)
    g = int((gimp_g / 100) * 255)
    b = int((gimp_b / 100) * 255)
    return (r, g, b)

def verificar_cor(pixel, cor_alvo, tolerancia=15):
    """Auxiliar para verificar se um pixel corresponde à cor alvo dentro da tolerância"""
    if len(pixel) == 4:  # RGBA
        r, g, b, a = pixel
    else:  # RGB
        r, g, b = pixel[:3]
    
    return (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia)

def encontrar_faixa_azul(imagem, cor_alvo_ignorado, tolerancia=15):
    """
    Procura os três padrões visuais verticais solicitados analisando uma pequena 
    margem na lateral direita para evitar problemas com desalinhamentos na imagem.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    cor_escura = (35, 31, 32)
    cor_branca = (255, 255, 255)
    
    posicoes_corte = []
    
    y = 0
    while y < altura - 20:
        padrao_encontrado_nesta_linha = False
        
        # Varre as colunas de X do pixel (largura-15) até (largura-2) para cobrir variações de margem
        for x in range(largura - 15, largura - 1):
            if x < 0: continue
            
            # --- PASSO 1: Medir a primeira faixa escura ---
            h1 = 0
            while y + h1 < altura and verificar_cor(pixels[x, y + h1], cor_escura, tolerancia):
                h1 += 1
                if h1 > 7: break
                
            # --- PASSO 2: Medir a faixa branca logo após h1 ---
            h2 = 0
            while y + h1 + h2 < altura and verificar_cor(pixels[x, y + h1 + h2], cor_branca, tolerancia):
                h2 += 1
                if h2 > 7: break
                
            # --- PASSO 3: Medir a segunda faixa escura logo após h1 + h2 ---
            h3 = 0
            while y + h1 + h2 + h3 < altura and verificar_cor(pixels[x, y + h1 + h2 + h3], cor_escura, tolerancia):
                h3 += 1
                if h3 > 7: break

            # --- VALIDAÇÃO DOS TRÊS PADRÕES ---
            e_padrao_1 = (h1 == 4 and h2 == 4 and h3 == 5)
            e_padrao_2 = (h1 == 5 and h2 == 4 and h3 == 4)
            e_padrao_3 = (h1 == 4 and h2 == 4 and h3 == 4)

            if e_padrao_1 or e_padrao_2 or e_padrao_3:
                posicao_corte = y - 30
                if posicao_corte < 0:
                    posicao_corte = 0
                    
                # EVITA DUPLICADOS: Margem mínima de 40px entre uma questão e outra
                if not posicoes_corte or (posicao_corte - posicoes_corte[-1] > 40):
                    posicoes_corte.append(posicao_corte)
                    print(f"Padrão detectado em y={y} (coluna x={x}) [Escuro:{h1}px, Branco:{h2}px, Escuro:{h3}px] -> Cortando em y={posicao_corte}")
                
                padrao_encontrado_nesta_linha = True
                break # Sai do loop de X pois já achou o corte para este "y"
        
        if padrao_encontrado_nesta_linha:
            # Se achou, pula 10 pixels para avançar além do marcador físico e não reanalisar a mesma linha
            y += 10 
        else:
            y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_faixa_azul(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhum dos padrões visuais especificados foi detectado.")
        return
    
    print(f"Encontradas {len(posicoes_corte)} correspondências para corte")
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        posicao_anterior = posicao_corte
    
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"
    pasta_saida = "questoes_colunas"
    
    cor_do_padrao = (35, 31, 32) 
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    print("Divisão concluída!")