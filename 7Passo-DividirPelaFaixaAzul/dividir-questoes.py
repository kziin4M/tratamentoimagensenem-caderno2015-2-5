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
    """
    Verifica se a cor do pixel está dentro da tolerância da cor alvo
    """
    if len(pixel) == 4:  # RGBA
        r, g, b, a = pixel
    else:  # RGB
        r, g, b = pixel[:3]
        
    return (abs(r - cor_alvo[0]) <= tolerancia and 
            abs(g - cor_alvo[1]) <= tolerancia and 
            abs(b - cor_alvo[2]) <= tolerancia)

def encontrar_faixa_azul(imagem, tolerancia_cor=15):
    """
    Encontra posições seguindo o novo padrão composto por 3 faixas verticais:
    - Faixa 1: (35, 31, 32) -> 4px (margem: 2px a 6px)
    - Faixa 2: (255, 255, 255) -> 4px (margem: 2px a 6px)
    - Faixa 3: (35, 31, 32) -> 5px (margem: 3px a 7px)
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    cor_escura = (35, 31, 32)
    cor_clara = (255, 255, 255)
    
    y = 0
    while y < altura - 15: # 15 é a soma aproximada das alturas mínimas
        # Analisa a sequência vertical a partir do ponto 'y' atual
        atual_y = y
        
        # 1. Validar primeira faixa (35, 31, 32) - Alvo: 4px (min 2px, max 6px)
        cont_f1 = 0
        while atual_y < altura and verificar_cor(pixels[largura-2, atual_y], cor_escura, tolerancia_cor):
            cont_f1 += 1
            atual_y += 1
            if cont_f1 > 6: break
            
        if not (2 <= cont_f1 <= 6):
            y += 1
            continue
            
        # 2. Validar segunda faixa (255, 255, 255) - Alvo: 4px (min 2px, max 6px)
        cont_f2 = 0
        while atual_y < altura and verificar_cor(pixels[largura-2, atual_y], cor_clara, tolerancia_cor):
            cont_f2 += 1
            atual_y += 1
            if cont_f2 > 6: break
            
        if not (2 <= cont_f2 <= 6):
            y += 1
            continue
            
        # 3. Validar terceira faixa (35, 31, 32) - Alvo: 5px (min 3px, max 7px)
        cont_f3 = 0
        while atual_y < altura and verificar_cor(pixels[largura-2, atual_y], cor_escura, tolerancia_cor):
            cont_f3 += 1
            atual_y += 1
            if cont_f3 > 7: break
            
        if not (3 <= cont_f3 <= 7):
            y += 1
            continue
            
        # Se passou por todas as validações, o padrão completo foi encontrado!
        altura_total_padrao = cont_f1 + cont_f2 + cont_f3
        posicao_corte = y - 13
        if posicao_corte < 0:
            posicao_corte = 0
            
        posicoes_corte.append((posicao_corte, altura_total_padrao))
        print(f"Padrão encontrado começando em y={y} (F1:{cont_f1}px, F2:{cont_f2}px, F3:{cont_f3}px), cortando em y={posicao_corte}")
        
        # Pula o padrão inteiro encontrado para evitar re-detecção
        y += altura_total_padrao
        
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Divide a imagem verticalmente cortando ANTES das faixas detectadas
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_faixa_azul(imagem)
    
    if not posicoes_corte:
        print("Nenhum padrão visual encontrado na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} faixas para corte")
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, (posicao_corte, altura_padrao) in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # Avança a posição pulando o padrão visual encontrado nesta iteração
        posicao_anterior = posicao_corte + 13 + altura_padrao
    
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

    # caminho_imagem = "./inteiras/pagina_enem_15.png"  
    # pasta_saida = "pagina_15" 
    
    # Executa a divisão (a cor alvo já está definida internamente no novo padrão estruturado)
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida)
    
    print("Divisão concluída!")











    """
Propósito: Dividir as questões por padrão. Observa-se que ao início de cada questão tem uma faixa de alguma cor, que é o padrão de início de cada questão
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026

OBS1: puxe a imagem "colunas_concatenadas_verticalmente.png" do passo 6 para essa pasta do passo 7, e as imagens de páginas inteiras da pasta "inteiras" do passo 5 para essa pasta do passo 7

OBS2: este código foi originalmente preparado para percorrer cada pixel de cima para baixo, analizando o penúltimo pixel da direita, procurando por um padrão visual vertical de 10 pixels RGB 0-255 (64, 193, 243), seguido de 7 pixels RGB 0-255 (179, 230, 250), 4 px  RGB 0-255 (64, 193, 243) e 8 px RGB 0-255 (179, 230, 250). Quando encontrava esse padrão, cortava-se 13 pixels acima de começar o padrão.

OBS3: você vai precisar identificar o padrão visual que indica o começo da questão na sua prova usando o GIMP. Pode usar IA para mudar minimamente o código a fim de cortar sua imagem seguindo o padrão visual vertical da sua prova.

OBS4: você vai rodar esse código para cortar a imagem de colunas concatenadas, depois você vai rodar para cada página inteira

OBS5: atualize as linhas 130 e 134 para recortar a imagem de colunas concatenadas, depois atualize para recortar cada página inteira. Atualize o nome da pasta de saída também
"""

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

def encontrar_faixa_azul(imagem, cor_alvo, tolerancia=15, altura_faixa=10): # ATUALIZAR a altura da faixa
    """
    Encontra posições onde há uma faixa horizontal da cor especificada
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Percorre a imagem de cima para baixo
    y = 0
    while y < altura - altura_faixa:
        # Verifica se há uma faixa de 'altura_faixa' pixels da cor alvo
        faixa_encontrada = True
        
        for dy in range(altura_faixa):
            # Pega a cor do pixel atual (verifica no último pixel da linha, ou seja, no canto da imagem)
            pixel = pixels[largura-2, y + dy]  # CORRIGIDO: verificar o pixel próximo ao canto para evitar bordas
            
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            # Verifica se a cor está dentro da tolerância
            if (abs(r - cor_alvo[0]) > tolerancia or 
                abs(g - cor_alvo[1]) > tolerancia or 
                abs(b - cor_alvo[2]) > tolerancia):
                faixa_encontrada = False
                break
        
        if faixa_encontrada:
            # Corta ANTES da faixa azul (no pixel anterior)
            posicao_corte = y - 13  # CORREÇÃO: definir a variável
            if posicao_corte < 0:  # Evitar posições negativas
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Faixa azul encontrada começando em y={y}, cortando em y={posicao_corte}")
            # Pula a faixa inteira para evitar detecções múltiplas
            y += altura_faixa
        else:
            y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente cortando ANTES das faixas
    """
    # Abre a imagem
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições das faixas azuis
    posicoes_corte = encontrar_faixa_azul(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhuma faixa azul encontrada na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} faixas azuis para corte")
    
    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Corta as seções da imagem
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        # Garantir que a posição de corte é válida
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta a seção ANTES da faixa azul (do início anterior até o início da faixa)
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        # Salva a imagem cortada
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # A próxima seção começa após o final desta faixa azul
        posicao_anterior = posicao_corte + 10  # Pula a faixa azul de 10 pixels
    
    # Corta a seção final (após a última faixa azul)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "questoes_colunas" # Substitua pelo nome da pasta de saída desejada (questoes_colunas, pagina_15, pagina_28)

    #caminho_imagem = "./inteiras/pagina_enem_15.png"  # Substitua pelo caminho da sua imagem
    #pasta_saida = "pagina_15" # Substitua pelo nome da pasta de saída desejada (questoes_colunas, pagina_15, pagina_28)
    
    # Converte a cor do GIMP 0a100 para RGB (0a255)
    cor_do_padrao = converter_cor_gimp_para_rgb(25.1, 75.7, 95.3) # COLOCAR O RGB CORRETO DA FAIXA QUE DIVIDE AS QUESTÕES (0a100 do GIMP)
    print(f"Cor convertida: RGB{cor_do_padrao}")
    
    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    
    print("Divisão concluída!")


mude minimamente o codigo para procurar o padrao visual vertical de 4px rgb 0-255 (35,31,32), seguido de 4px rgb 0-255 (255,255,255), seguido de 5px rgb 0-255 (35,31,32). considere 2px de margem de erro, para mais e para menos de cada uma das faixas citadas do padrao visual vertical.