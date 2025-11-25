# utils/data_loader.py
import os
import unicodedata
import pandas as pd
import chardet
from io import StringIO

def detectar_encoding(caminho):
    with open(caminho, "rb") as f:
        raw = f.read(50000)
    enc = chardet.detect(raw).get("encoding") or "latin1"
    return enc

def _limpar_colname(c):
    if pd.isna(c):
        return ""
    s = str(c)
    s = s.replace("\ufeff", "").replace("\xa0", " ").strip()
    return s

def _try_parse_double_header(path, encoding):
    """
    Tenta detectar header duplo (linha de grupos + linha de colnames).
    Retorna df com colnames combinados (Group_Sub).
    """
    # ler primeiras 8 linhas sem header
    raw = pd.read_csv(path, encoding=encoding, header=None, nrows=12, engine="python")
    # encontrar primeira linha plausível de header (contendo 'Season' ou 'Age' ou 'Squad')
    header_idx = None
    for i in range(min(8, len(raw))):
        row = raw.iloc[i].astype(str).str.lower().tolist()
        if any(x in row for x in ("season", "age", "squad")):
            header_idx = i
            break

    if header_idx is None:
        return None

    # se a linha anterior existir e tiver muitos blanks, pode haver header duplo em header_idx-1
    group_idx = header_idx - 1 if header_idx - 1 >= 0 else None

    # read full with header at header_idx
    df = pd.read_csv(path, encoding=encoding, header=header_idx, engine="python")
    # clean column names
    cols = [ _limpar_colname(c) for c in df.columns ]
    # if group row exists, try to combine
    if group_idx is not None:
        try:
            group_row = raw.iloc[group_idx].astype(str).tolist()
            # normalize group names
            group_row = [g.strip() for g in group_row]
            # combine group + col
            new_cols = []
            for grp, col in zip(group_row, cols):
                g = grp.strip()
                if g == "" or g.lower() in ("nan", "None".lower()):
                    new_cols.append(col)
                else:
                    # avoid duplicates
                    label = f"{g}_{col}".strip("_")
                    new_cols.append(label)
            df.columns = [ _limpar_colname(c) for c in new_cols ]
        except Exception:
            df.columns = cols
    else:
        df.columns = cols

    return df

def carregar_csv(caminho):
    try:
        df = pd.read_csv(caminho, encoding="utf-8", engine="python")
    except:
        df = pd.read_csv(caminho, encoding="latin1", engine="python")

    # remover linhas totalmente vazias
    df = df.dropna(how="all")

    # converter todas as colunas para string primeiro
    df = df.astype(str)

    # limpar Season automaticamente
    if "Season" in df.columns:
        df["Season"] = (
            df["Season"]
            .fillna("")
            .astype(str)
            .str.replace("\.0$", "", regex=True)
            .str.replace("nan", "", regex=False)
            .str.replace("None", "", regex=False)
            .str.strip()
        )

    return df
