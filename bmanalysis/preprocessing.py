# basic preprocessing functions
import pandas as pd
import re
import pprint
import json


def get_unique_serie(df: pd.DataFrame, colname: str):
    "get unique values of given column as a serie"
    return pd.Series(df[colname].unique())


def get_uvals(uval: str, is_sep: bool = True) -> set:
    "uval"
    uvals = set()
    if ";" in uval:
        if is_sep:
            for t in uval.split(";"):
                uvals.add(t.strip() if t else "")
        else:
            uvals.add(uval.strip() if uval else "")
    else:
        uvals.add(uval)
    return uvals


def get_unique_values(df: pd.DataFrame, colname: str, is_sep: bool = True) -> set:
    "get object type values inside data frame"
    dfo_type = get_unique_serie(df, colname)
    otypes = set()
    for do in dfo_type:
        uvals = get_uvals(do, is_sep)
        otypes = otypes.union(uvals)
    return otypes


def get_nb(s: str) -> float:
    "find number in string"
    nb_matcher = re.compile(r"\d+(?:\.\d+)?")
    ss = nb_matcher.search(s)
    if ss is None:
        return
    else:
        return float(ss.group(0))


def get_unit(s: str) -> str:
    "get unit from dimension string"
    units = [" meter", " centimetres", "cm", "m"]
    for u in units:
        if u in s:
            return u[1:].lower() if u != "m" else u


def get_dimension_type(s: str) -> str:
    "get dimension type from dimension part"
    return s.split(":").pop(0).strip().lower()


def get_dimension(col_value: str) -> dict:
    "get dimension"
    dims = {}
    for value in col_value.split(";"):
        vtype = get_dimension_type(value)
        v_val = get_nb(value)
        vunit = get_unit(value)
        dims[vtype] = (vunit, v_val)
    return dims


def parse_dimension(df: pd.DataFrame):
    "parse dimensions inside dataframe"
    dfcol = get_unique_serie(df, colname="Dimensions")
    ds = set()
    dnames = set()
    dunits = set()
    for colvalue in dfcol:
        dimensions = get_dimension(colvalue)
        for dname, (dunit, dvals) in dimensions.items():
            dunits.add(dunit)
            dnames.add(dname)
        dims = sorted(list(dimensions.items()), key=lambda x: x[0])
        ds.add(tuple(dims))
    return ds, dnames, dunits


class DimensionPart:
    "Dimension Part"

    def __init__(self, n: str, v: float, u: str):
        self.name = n
        self.value = v
        self.unit = u

    def to_dict(self):
        return {self.name: {self.unit: self.value}}

    def to_tuple(self):
        return (self.name, self.unit, self.value)


def get_date_value(s: str):
    dval = get_nb(s)
    if dval is None:
        return
    supp = s.upper()
    if "THC" in supp:
        dval = 100 * dval
    if "BC" in supp:
        return -dval
    elif "AD" in s.upper():
        return dval
    else:
        return dval


def is_circa(s: str):
    "if circa contained within string"
    return "circa" in s


def get_date_part(s: str, nb: int):
    "date part"
    splited = s.split("-")
    if len(splited) == 1:
        return splited.pop(0)
    else:
        return splited.pop(nb)


def get_start_date(s: str):
    "start date"
    dval = get_date_value(get_date_part(s, 0))
    if dval is None:
        return dval
    else:
        return int(dval)


def get_end_date(s: str):
    "end date"
    dval = get_date_value(get_date_part(s, 1))
    if dval is None:
        print(s)
        print(dval)
    else:
        return int(dval)


def get_date(s: str):
    "get date"
    d = {}
    d["start"] = None
    d["end"] = None
    d["is_circa"] = False
    if "Sixth century BC" == s:
        d["start"] = -599
        d["end"] = -500
        return d
    elif "(mid-late)5thC BC" == s:
        d["start"] = -450
        d["end"] = -400
        return d
    elif "Fourth century BC (?)" == s:
        d["start"] = -399
        d["end"] = -300
        d["is_circa"] = True
        return d
    elif "Fifth century BC (?)" == s:
        d["start"] = -499
        d["end"] = -400
        d["is_circa"] = True
        return d
    else:
        d["start"] = get_start_date(s)
        d["end"] = get_end_date(s)
        d["is_circa"] = is_circa(s)
        return d


def get_dates(dates: pd.Series):
    ""
    ds = set()
    for d in dates:
        ddict = get_date(d)
        dtpl = tuple(sorted(list(ddict.items()), key=lambda x: (x[0], x[1])))
        ds.add(dtpl)
    return ds


def dfjsonable(df_dict):
    dd = {}
    row_nb = len(df_dict["Image"])
    for key, values in df_dict.items():
        dd[key] = []
        if "Production date" in key:
            for val in values.values():
                if pd.isna(val) is False:
                    d = get_date(val)
                    dd[key].append(d)
                else:
                    dd[key].append(val)
        elif "Dimensions" in key:
            for val in values.values():
                if pd.isna(val) is False:
                    d = get_dimension(val)
                    dd[key].append(d)
                else:
                    dd[key].append(val)
        elif "Object type" in key:
            for val in values.values():
                if pd.isna(val) is False:
                    d = get_uvals(val, is_sep=True)
                    dd[key].append(list(d))
                else:
                    dd[key].append(val)
        elif "Culture" in key:
            for val in values.values():
                if pd.isna(val) is False:
                    d = get_uvals(val, is_sep=True)
                    dd[key].append(list(d))
                else:
                    dd[key].append(val)
        elif "Technique" in key:
            for val in values.values():
                if pd.isna(val) is False:
                    d = get_uvals(val, is_sep=True)
                    dd[key].append(list(d))
                else:
                    dd[key].append(val)
        else:
            for val in values.values():
                dd[key].append(val)
    return dd


def wjson(dd, path="./data/EgyptBritishMuseum-2021-03-05v2.json"):
    with open(path, "w", encoding="utf-8") as f:
        js = json.dumps(dd, ensure_ascii=False, indent=2)
        f.write(js)

if __name__ == "__main__":
    path = "./data/EgyptBritishMuseum-2021-03-05CSVUnique.csv"
    df = pd.read_csv(path)
    df_dict = df.to_dict()
    dd = dfjsonable(df_dict)
    # wjson(dd) # be sure to change path before uncommenting
