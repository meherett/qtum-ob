#!/usr/bin/env python3

"""
Title        : QtumOB - (Qtum Orphan Block)
Description  : Qtum blockchain orphan block finder for all Qtum core debug files.
Author       : Meheret Tesfaye Batu <meherett@zoho.com>
"""

from pandas import DataFrame
from typing import Optional, List
from os import path
from tqdm import tqdm

import requests
import json
import warnings

# UpdateTip, ThreadStakeMiner
_ = ("UpdateTip", "ThreadStakeMiner", "CreateNewBlock")
# Ignore all warnings
warnings.filterwarnings('ignore')


class QtumOB:  # Qtum Orphan Block

    def __init__(self, config: dict):

        self.datas: List[dict] = []
        self.config: dict = config

    def read_debug_lines(self, name: str) -> List[str]:
        debug_path: str = path.abspath(path.join(base_path, self.config["debugs_directory"], name))
        with open(debug_path, "r", encoding="utf-8") as debug_data:
            lines: List[str] = debug_data.readlines()
            debug_data.close()
        return lines

    def do_operations(self, lines: List[str], line_type: str) -> "QtumOB":
        for index, line in enumerate(lines):
            if line_type in line and line_type in _:
                split_debug: List[str] = line[:-1].split(" ")
                length_split_debug: int = len(split_debug)

                if length_split_debug == 21 and line_type in line and _[2] not in line:
                    data = dict(new=split_debug[0])
                    for i, detail_split_debug in enumerate(split_debug):
                        if i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                            continue
                        _split_debug = detail_split_debug.split("=")
                        data.setdefault(_split_debug[0], _split_debug[1])
                    self.datas.append(data)
                elif length_split_debug == 11:
                    data = dict(new=split_debug[0])
                    for i, detail_split_debug in enumerate(split_debug):
                        if i in [0, 1, 2]:
                            continue
                        _split_debug = detail_split_debug.split("=")
                        data.setdefault(_split_debug[0], _split_debug[1])
                    self.datas.append(data)
            elif line_type in line:
                pass
        return self


def main(config: dict):

    if config["progress_bar"]:
        tqdm.pandas()
    for debug in config["debugs"]:
        qtum_ob: QtumOB = QtumOB(config)
        lines: List[str] = qtum_ob.read_debug_lines(name=debug["debug_name"])
        for line in debug["lines"]:
            qtum_ob.do_operations(lines=lines, line_type=line["type"])
            data_frame: DataFrame = DataFrame(qtum_ob.datas)
            if line["duplicated_height"] and line["type"] in _:
                data_frame = data_frame[data_frame.duplicated(['height'], keep=False)]
                if config["progress_bar"]:
                    data_frame["orphan_block"] = data_frame[0:20]['best'].progress_apply(is_orphan_block)
                else:
                    data_frame["orphan_block"] = data_frame[0:20]['best'].apply(is_orphan_block)
            elif not line["duplicated_height"] and line["type"] in _:
                if config["progress_bar"]:
                    data_frame["orphan_block"] = data_frame[0:20]['best'].progress_apply(is_orphan_block)
                else:
                    data_frame["orphan_block"] = data_frame[0:20]['best'].apply(is_orphan_block)
            data_frame.to_excel(f"{line['save_name']}.xlsx", index=True)


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
    def is_orphan_block(block_id: str, headers: dict = CONFIG["headers"], timeout: int = CONFIG["timeout"]) -> bool:
        mainnet_url: str = f"https://qtum.info/api/block/{block_id}"
        testnet_url: str = f"https://testnet.qtum.info/api/block/{block_id}"
        url: str = mainnet_url if CONFIG["network"] == "mainnet" else testnet_url
        response: requests.models.Response = requests.get(
            url=url, headers=headers, timeout=timeout
        )
        if response.status_code == 200:
            return response.json()["hash"] != block_id
        return True

    # Run main
    main(config=CONFIG)
