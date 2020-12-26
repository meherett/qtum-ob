#!/usr/bin/env python3

"""
Title        : QtumOB - (Qtum Orphan Block)
Description  : Qtum blockchain orphan block finder for all Qtum core debug files.
Author       : Meheret Tesfaye Batu <meherett@zoho.com>
"""

from pandas import DataFrame, ExcelWriter, Series
from typing import Optional, List, Tuple
from os import path
from tqdm import tqdm

import requests
import json
import warnings

# UpdateTip, ThreadStakeMiner
_ = ("UpdateTip", "ThreadStakeMiner", "CreateNewBlock", "CBlock")
# Ignore all warnings
warnings.filterwarnings('ignore')


class QtumOB:  # Qtum Orphan Block

    def __init__(self, config: dict):

        self.datas: List[dict] = []
        self.config: dict = config

    def read_lines(self, name: str) -> List[str]:
        debug_path: str = path.abspath(path.join(base_path, self.config["debugs_dir"], name))
        with open(debug_path, "r", encoding="utf-8") as debug_data:
            lines: List[str] = debug_data.readlines()
            debug_data.close()
        return lines

    def filter_lines(self, lines: List[str], filters: List[str]) -> "QtumOB":
        for index, line in enumerate(lines):
            for _filter in filters:
                if _filter in line and _filter in _[0]:
                    split_debug: List[str] = line[:-1].split(" ")
                    length_split_debug: int = len(split_debug)
                    if length_split_debug == 21 and _filter in line and _[2] not in line:
                        data = dict()
                        for i, detail_split_debug in enumerate(split_debug):
                            if i == 13:
                                _split_debug = detail_split_debug.split("=")
                                data.setdefault("Hash", _split_debug[1])
                            # elif i in [14, 15]:
                            #     _split_debug = detail_split_debug.split("=")
                            #     data.setdefault(_split_debug[0], _split_debug[1])
                        self.datas.append(data)
                    elif length_split_debug == 11:
                        data = dict()
                        for i, detail_split_debug in enumerate(split_debug):
                            if i == 3:
                                _split_debug = detail_split_debug.split("=")
                                data.setdefault("Hash", _split_debug[1])
                            # elif i in [4, 5]:
                            #     _split_debug = detail_split_debug.split("=")
                            #     data.setdefault(_split_debug[0], _split_debug[1])
                        self.datas.append(data)
                elif _filter in line and _filter in _[3]:
                    split_debug: List[str] = line[:-1].split(" ")
                    length_split_debug: int = len(split_debug)
                    if length_split_debug == 15 and _filter in line:
                        data = dict(date=split_debug[0], update_tip=False, cblock=True)
                        # for i, detail_split_debug in enumerate(split_debug):
                        #     if i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                        #         continue
                        #     _split_debug = detail_split_debug.split("=")
                        #     data.setdefault(_split_debug[0], _split_debug[1])
                        # self.datas.append(data)
        return self


def main(config: dict):

    for debug in config["debugs"]:
        qtum_ob: QtumOB = QtumOB(config)
        lines: List[str] = qtum_ob.read_lines(name=debug["debug_name"])
        qtum_ob.filter_lines(lines=lines, filters=debug["filters"])
        data_frame: DataFrame = DataFrame(qtum_ob.datas)
        tqdm.pandas(desc=f"{debug['debug_name']}")
        data_frame[["Orphan Block", "Block Height"]] = data_frame[0:3]['Hash'].progress_apply(is_orphan_block)
        excel_writer = ExcelWriter(f"{debug['save_name']}.xlsx", engine="xlsxwriter")
        data_frame.to_excel(excel_writer, sheet_name='SheetQtumOB', index=False, na_rep="None")
        _format = excel_writer.book.add_format({'align': 'center'})
        excel_writer.sheets['SheetQtumOB'].set_column(
            data_frame.columns.get_loc('Hash'), data_frame.columns.get_loc('Hash'), 70, _format
        )
        excel_writer.sheets['SheetQtumOB'].set_column(
            data_frame.columns.get_loc('Orphan Block'), data_frame.columns.get_loc('Orphan Block'), 15, _format
        )
        excel_writer.sheets['SheetQtumOB'].set_column(
            data_frame.columns.get_loc("Block Height"), data_frame.columns.get_loc("Block Height"), 15, _format
        )
        excel_writer.save()


if __name__ == '__main__':

    # Read configuration
    base_path: str = path.dirname(__file__)
    config_path: str = path.abspath(path.join(base_path, "config.json"))
    with open(config_path, "r", encoding="utf-8") as config_data:
        CONFIG: dict = json.loads(config_data.read())
        config_data.close()

    # Check Qtum network type
    if CONFIG["network"] not in ["mainnet", "testnet"]:
        raise ValueError("Invalid Qtum network, Please choose only 'mainnet' or 'testnet' networks.")

    # Check orphan block check on Qtum blockchain
    def is_orphan_block(block_id: str, headers: dict = CONFIG["headers"],
                        timeout: int = CONFIG["timeout"]) -> Series:
        mainnet_url: str = f"https://qtum.info/api/block/{block_id}"
        testnet_url: str = f"https://testnet.qtum.info/api/block/{block_id}"
        url: str = mainnet_url if CONFIG["network"] == "mainnet" else testnet_url
        response: requests.models.Response = requests.get(
            url=url, headers=headers, timeout=timeout
        )
        if response.status_code == 200:
            return Series([response.json()["hash"] != block_id, response.json()["height"]])
        return Series([True, None])

    # Run main
    main(config=CONFIG)
