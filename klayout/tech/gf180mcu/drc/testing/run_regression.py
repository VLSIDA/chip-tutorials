# Copyright 2022 GlobalFoundries PDK Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Run GlobalFoundries 180nm MCU DRC Unit Regression.

Usage:
    run_regression.py (--help| -h)
    run_regression.py [--mp=<num>] [--run_dir=<run_dir_path>] [--table_name=<table_name>]

Options:
    --help -h                           Print this help message.
    --mp=<num>                          The number of threads used in run.
    --run_dir=<run_dir>                 Run directory to save all the results.
    --table_name=<table_name>           Target specific table.
"""

from subprocess import check_call
from subprocess import Popen, PIPE
import concurrent.futures
import traceback
import yaml
from docopt import docopt
import os
from datetime import datetime
import xml.etree.ElementTree as ET
import time
import pandas as pd
import logging
import glob
from pathlib import Path
from tqdm import tqdm
import re
import gdstk
import errno
import numpy as np
from collections import defaultdict


SUPPORTED_TC_EXT = "gds"
SUPPORTED_SW_EXT = "yaml"
RULE_LAY_NUM = 10000
PATH_WIDTH = 0.01
RULE_STR_SEP = "--"
ANALYSIS_RULES = [
    "pass_patterns",
    "fail_patterns",
    "false_negative",
    "false_positive",
    "not_tested",
]


def get_unit_test_coverage(gds_file):
    """
    This function is used for getting all test cases available inside a single test table.
    Parameters
    ----------
    gds_file : str
        Path string to the location of unit test cases path.
    Returns
    -------
    list
        A list of unique rules found.
    """
    # Get rules from gds
    rules = []

    # layer num of rule text
    lay_num = 11
    # layer data type of rule text
    lay_dt = 222

    # Getting all rules names from testcase
    library = gdstk.read_gds(gds_file)
    top_cells = library.top_level()  # Get top cells
    for cell in top_cells:
        flatten_cell = cell.flatten()
        # Get all text labels for each cell
        labels = flatten_cell.get_labels(
            apply_repetitions=True, depth=None, layer=lay_num, texttype=lay_dt
        )
        # Get label value
        for label in labels:
            rule = label.text
            if rule not in rules:
                rules.append(rule)

    return rules


def check_klayout_version():
    """
    check_klayout_version checks klayout version and makes sure it would work with the DRC.
    """
    # ======= Checking Klayout version =======
    klayout_v_ = os.popen("klayout -b -v").read()
    klayout_v_ = klayout_v_.split("\n")[0]
    klayout_v_list = []

    if klayout_v_ == "":
        logging.error("Klayout is not found. Please make sure klayout is installed.")
        exit(1)
    else:
        klayout_v_list = [int(v) for v in klayout_v_.split(" ")[-1].split(".")]

    if len(klayout_v_list) < 1 or len(klayout_v_list) > 3:
        logging.error("Was not able to get klayout version properly.")
        exit(1)
    elif len(klayout_v_list) >= 2 or len(klayout_v_list) <= 3:
        if klayout_v_list[1] < 28 or (klayout_v_list[1] == 28 and klayout_v_list[2] <= 3):
            logging.error("Prerequisites at a minimum: KLayout 0.28.4")
            logging.error(
                "Using this klayout version is not supported in this development."
            )
            exit(1)

    logging.info(f"Your Klayout version is: {klayout_v_}")


def get_switches(yaml_file, rule_name):
    """Parse yaml file and extract switches data
    Parameters
    ----------
    yaml_file : str
            yaml config file path given py the user.
    Returns
    -------
    yaml_dic : dictionary
            dictionary containing switches data.
    """

    # load yaml config data
    with open(yaml_file, "r") as stream:
        try:
            yaml_dic = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    return [f"{param}={value}" for param, value in yaml_dic[rule_name].items()]


def parse_results_db(results_database):
    """
    This function will parse Klayout database for analysis.

    Parameters
    ----------
    results_database : string or Path object
        Path string to the results file

    Returns
    -------
    set
        A set that contains all rules in the database with or without violations
    """

    mytree = ET.parse(results_database)
    myroot = mytree.getroot()

    # Initial values for counter
    rule_counts = defaultdict(int)

    # Get the list of all rules that ran regardless it generated output or not
    for z in myroot[5]:
        rule_name = f"{z[0].text}"
        rule_counts[rule_name] = 0

    # Count rules with violations.
    for z in myroot[7]:
        rule_name = f"{z[1].text}".replace("'", "")
        rule_counts[rule_name] += 1

    return rule_counts


def parse_results_db_splitted(results_database):
    """
    This function will parse Klayout database for analysis.

    Parameters
    ----------
    results_database : string or Path object
        Path string to the results file
    Returns
    -------
    set
        A set that contains all rules in the database with violations
    """

    mytree = ET.parse(results_database)
    myroot = mytree.getroot()

    all_violating_rules = set()

    for z in myroot[7]:  # myroot[7] : List rules with viloations
        all_violating_rules.add(f"{z[1].text}".replace("'", ""))

    return all_violating_rules


def analyze_splitted_results(layout_path, pattern_results, test_criteria):
    """
    This function run a single test case using the correct DRC file.

    Parameters
    ----------
    layout_path : stirng or Path object
        Path string to the layout of the test pattern we want to test.
    pattern_results : stirng or Path object
        Path to the location where is the result db file of DRC run is generated.
    test_criteria : string
        Type of test that we are running on.

    Returns
    -------
    dict
        A dict with all rule counts
    """

    # Initial value for counters
    rule_counts = defaultdict(int)

    # Get test rule name
    test_rule_path = Path(layout_path).parents[1]
    test_rule = os.path.basename(test_rule_path)

    # Get pass/fail patterns counts
    pass_patterns = os.path.join(test_rule_path, "pass", "*.gds")
    fail_patterns = os.path.join(test_rule_path, "fail", "*.gds")
    pass_count = len(glob.glob(str(pass_patterns)))
    fail_count = len(glob.glob(str(fail_patterns)))

    if len(pattern_results) > 0:
        violated_rules = set()
        for p in pattern_results:
            rules_with_violations = parse_results_db_splitted(p)
            violated_rules.update(rules_with_violations)

        if test_criteria == "pass":
            if test_rule in violated_rules:
                # false positive
                return {f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[0]}': pass_count, f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[1]}': fail_count,
                        f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[3]}': 1, f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[2]}': 0,
                        f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[4]}': 0}
            else:
                # true positive
                return {f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[0]}': pass_count, f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[1]}': fail_count,
                        f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[3]}': 0, f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[2]}': 0,
                        f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[4]}': 0}
        else:
            if test_rule in violated_rules:
                # true negative
                return {f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[0]}': pass_count, f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[1]}': fail_count,
                        f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[3]}': 0, f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[2]}': 0,
                        f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[4]}': 0}
            else:
                # false negative
                return {f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[0]}': pass_count, f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[1]}': fail_count,
                        f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[3]}': 0, f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[2]}': 1,
                        f'{test_rule}{RULE_STR_SEP}{ANALYSIS_RULES[4]}': 0}
    else:
        return rule_counts


def run_test_case(
    drc_dir,
    layout_path,
    run_dir,
    testcase_basename,
    table_name,
    test_criteria,
):
    """
    This function run a single test case using the correct DRC file.

    Parameters
    ----------
    drc_dir : string or Path
        Path to the location where all runsets exist.
    layout_path : stirng or Path object
        Path string to the layout of the test pattern we want to test.
    run_dir : stirng or Path object
        Path to the location where is the regression run is done.
    testcase_basename : string
        Testcase name that we are running on.
    table_name : string
        Table name that we are running on.
    test_criteria : string
        Type of test that we are running on.

    Returns
    -------
    dict
        A dict with all rule counts
    """

    # Initial value for counters
    rule_counts = defaultdict(int)

    # Get switches used for each run
    sw_file = os.path.join(
        Path(layout_path.parent).absolute(), f"{testcase_basename}.{SUPPORTED_SW_EXT}"
    )

    if os.path.exists(sw_file):
        switches = " ".join(get_switches(sw_file, testcase_basename))
    else:
        switches = "--variant=C"  # default switch

    # Adding switches for specific runsets
    if "antenna" in str(layout_path):
        switches += " --antenna_only"
    elif "density" in str(layout_path):
        switches += " --density_only"

    # Creating run folder structure
    pattern_clean = ".".join(os.path.basename(layout_path).split(".")[:-1])
    output_loc = f"{run_dir}/{table_name}"
    pattern_log = f"{output_loc}/{pattern_clean}_drc.log"

    # command to run drc
    call_str = f"python3 {drc_dir}/run_drc.py --path={layout_path} {switches} --table={table_name} --run_dir={output_loc} --run_mode=flat --thr=1  > {pattern_log} 2>&1"

    # Starting klayout run
    os.makedirs(output_loc, exist_ok=True)
    try:
        check_call(call_str, shell=True)
    except Exception as e:
        pattern_results = glob.glob(os.path.join(output_loc, f"{pattern_clean}*.lyrdb"))
        if len(pattern_results) < 1:
            logging.error("%s generated an exception: %s" % (pattern_clean, e))
            traceback.print_exc()
            raise Exception("Failed DRC run.")

    # dumping log into output to make CI have the log
    if os.path.isfile(pattern_log):
        logging.info("# Dumping drc run output log:")
        with open(pattern_log, "r") as f:
            for line in f:
                line = line.strip()
                logging.info(f"{line}")

    # Checking if run is completed or failed
    pattern_results = glob.glob(os.path.join(output_loc, f"{pattern_clean}*.lyrdb"))

    # Analysis of splitted testcases into patterns
    if test_criteria in ['pass' , 'fail']:
        return analyze_splitted_results(
            layout_path, pattern_results, test_criteria
        )

    else:
        # Get list of rules covered in the test case
        rules_tested = get_unit_test_coverage(layout_path)

        if len(pattern_results) > 0:
            # db to gds conversion
            marker_output, runset_analysis = convert_results_db_to_gds(
                pattern_results[0], rules_tested
            )

            # Generating merged testcase for violated rules
            merged_output = generate_merged_testcase(layout_path, marker_output)

            # Generating final db file
            if os.path.exists(merged_output):
                final_report = f'{merged_output.split(f".{SUPPORTED_TC_EXT}")[0]}_final.lyrdb'
                analysis_log = f'{merged_output.split(f".{SUPPORTED_TC_EXT}")[0]}_analysis.log'
                call_str = f"klayout -b -r {runset_analysis} -rd input={merged_output} -rd report={final_report}  > {analysis_log} 2>&1"

                failed_analysis_step = False

                try:
                    check_call(call_str, shell=True)
                except Exception as e:
                    failed_analysis_step = True
                    logging.error("%s generated an exception: %s" % (pattern_clean, e))
                    traceback.print_exc()

                # dumping log into output to make CI have the log
                if os.path.isfile(analysis_log):
                    logging.info("# Dumping analysis run output log:")
                    with open(analysis_log, "r") as f:
                        for line in f:
                            line = line.strip()
                            logging.info(f"{line}")

                if failed_analysis_step:
                    raise Exception("Failed DRC analysis run.")

                if os.path.exists(final_report):
                    rule_counts = parse_results_db(final_report)
                    return rule_counts
                else:
                    return rule_counts
            else:
                return rule_counts
        else:
            return rule_counts


def run_all_test_cases(tc_df, drc_dir, run_dir, num_workers):
    """
    This function run all test cases from the input dataframe.

    Parameters
    ----------
    tc_df : pd.DataFrame
        DataFrame that holds all the test cases information for running.
    drc_dir : string or Path
        Path string to the location of the drc runsets.
    run_dir : string or Path
        Path string to the location of the testing code and output.
    num_workers : int
        Number of workers to use for running the regression.

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame with all test cases information post running.
    """

    results_df_list = []
    tc_df["run_status"] = "no status"

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        future_to_run_id = dict()
        for i, row in tc_df.iterrows():
            future_to_run_id[
                executor.submit(
                    run_test_case,
                    drc_dir,
                    row["test_path"],
                    run_dir,
                    row["testcase_basename"],
                    row["table_name"],
                    row["test_criteria"],
                )
            ] = row["run_id"]

        for future in concurrent.futures.as_completed(future_to_run_id):
            run_id = future_to_run_id[future]
            try:
                rule_counts = future.result()
                if rule_counts:
                    rule_counts_df = pd.DataFrame(
                        {
                            "analysis_rule": rule_counts.keys(),
                            "count": rule_counts.values(),
                        }
                    )
                    rule_counts_df["rule_name"] = (
                        rule_counts_df["analysis_rule"].str.split(RULE_STR_SEP).str[0]
                    )
                    rule_counts_df["type"] = (
                        rule_counts_df["analysis_rule"].str.split(RULE_STR_SEP).str[1]
                    )
                    rule_counts_df.drop(columns=["analysis_rule"], inplace=True)
                    rule_counts_df["count"] = rule_counts_df["count"].astype(int)
                    rule_counts_df = rule_counts_df.pivot(
                        index="rule_name", columns="type", values="count"
                    )
                    rule_counts_df = rule_counts_df.fillna(0)
                    rule_counts_df = rule_counts_df.reset_index(drop=False)
                    rule_counts_df = rule_counts_df.rename(
                        columns={"index": "rule_name"}
                    )

                    rule_counts_df["table_name"] = tc_df.loc[
                        tc_df["run_id"] == run_id, "table_name"
                    ].iloc[0]

                    for c in ANALYSIS_RULES:
                        if c not in rule_counts_df.columns:
                            rule_counts_df[c] = 0

                    rule_counts_df[ANALYSIS_RULES] = rule_counts_df[
                        ANALYSIS_RULES
                    ].astype(int)
                    rule_counts_df = rule_counts_df[
                        ["table_name", "rule_name"] + ANALYSIS_RULES
                    ]
                    results_df_list.append(rule_counts_df)
                    tc_df.loc[tc_df["run_id"] == run_id, "run_status"] = "completed"
                else:
                    tc_df.loc[tc_df["run_id"] == run_id, "run_status"] = "no output"

            except Exception as exc:
                logging.error("%d generated an exception: %s" % (run_id, exc))
                traceback.print_exc()
                tc_df.loc[tc_df["run_id"] == run_id, "run_status"] = "exception"

    if len(results_df_list) > 0:
        results_df = pd.concat(results_df_list)
    else:
        results_df = pd.DataFrame()

    return results_df, tc_df


def parse_existing_rules(rule_deck_path, output_path, target_table=None):
    """
    This function collects the rule names from the existing drc rule decks.

    Parameters
    ----------
    rule_deck_path : string or Path object
        Path string to the DRC directory where all the DRC files are located.
    output_path : string or Path
        Path of the run location to store the output analysis file.
    target_table : string Optional
        Name of the table to be in testing

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame with the rule and rule deck used.
    """

    if target_table is None:
        drc_files = glob.glob(os.path.join(rule_deck_path, "rule_decks", "*.drc"))
    else:
        table_rule_file = os.path.join(
            rule_deck_path, "rule_decks", f"{target_table}.drc"
        )
        if not os.path.isfile(table_rule_file):
            logging.error(f"Unknown {target_table} table name is selected, please recheck")
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), table_rule_file
            )

        drc_files = [table_rule_file]

    rules_data = list()

    for runset in drc_files:
        if "split" in runset:
            continue
        with open(runset, "r") as f:
            for line in f:
                if ".output" in line:
                    line_list = line.split("'")
                    rule_info = dict()
                    rule_info["table_name"] = os.path.basename(runset).replace(
                        ".drc", ""
                    )
                    rule_info["rule_name"] = line_list[1]
                    rule_info["in_rule_deck"] = 1
                    rules_data.append(rule_info)

    df = pd.DataFrame(rules_data)
    df.drop_duplicates(inplace=True)
    df.to_csv(os.path.join(output_path, "rule_deck_rules.csv"), index=False)
    return df


def generate_merged_testcase(orignal_testcase, marker_testcase):
    """
    This function will merge orignal gds file with generated
    markers gds file.

    Parameters
    ----------
    orignal_testcase : string or Path object
        Path string to the orignal testcase

    marker_testcase : string or Path
        Path of the output marker gds file generated from db file.

    Returns
    -------
    merged_gds_path : string or Path
        Path of the final merged gds file generated.
    """

    new_lib = gdstk.Library()

    lib_org = gdstk.read_gds(orignal_testcase)
    lib_marker = gdstk.read_gds(marker_testcase)

    # Getting flattened top cells
    top_cell_org = lib_org.top_level()[0].flatten(apply_repetitions=True)
    top_cell_marker = lib_marker.top_level()[0].flatten(apply_repetitions=True)
    marker_polygons = top_cell_marker.get_polygons(
        apply_repetitions=True, include_paths=True, depth=None
    )

    # Merging all polygons of markers with original testcase
    for marker_polygon in marker_polygons:
        top_cell_org.add(marker_polygon)

    # Adding flattened merged cell
    new_lib.add(top_cell_org.flatten(apply_repetitions=True))

    # Writing final merged gds file
    merged_gds_path = f'{marker_testcase.replace(".gds", "")}_merged.gds'
    new_lib.write_gds(merged_gds_path)

    return merged_gds_path


def draw_polygons(polygon_data, cell, lay_num, lay_dt, path_width):
    """
    This function is used for drawing gds file with all violated polygons.

    Parameters
    ----------
    polygon_data : str
        Contains data points for each violated polygon
    cell: gdstk.Cell
        Top cell will contains all generated polygons
    lay_num: int
        Number of layer used to draw violated polygons
    lay_dt : int
        Data type of layer used to draw violated polygons
    path_width : float
        Width  will used to draw edges

    Returns
    -------
    None
    """

    # Cleaning data points
    polygon_data = re.sub(r"\s+", "", polygon_data)
    polygon_data = re.sub(r"[()]", "", polygon_data)

    tag_split = polygon_data.split(":")
    tag = tag_split[0]
    poly_txt = tag_split[1]
    polygons = re.split(r"[/|]", poly_txt)

    # Select shape type to be drawn
    if tag == "polygon":
        for poly in polygons:
            points = [
                (float(p.split(",")[0]), float(p.split(",")[1]))
                for p in poly.split(";")
            ]
            cell.add(gdstk.Polygon(points, lay_num, lay_dt))

    elif tag == "edge-pair":
        for poly in polygons:
            points = [
                [float(p.split(",")[0]), float(p.split(",")[1])]
                for p in poly.split(";")
            ]
            dist = np.sqrt(((points[0][0]) - (points[1][0]))**2 + ((points[0][1]) - (points[1][1]))**2)
            # Adding condition for extremely small edge length
            ## to generate a path to be drawn
            if dist < path_width:
                points[1][0] = points[0][0] + 2 * path_width
            cell.add(gdstk.FlexPath(points, path_width, layer=lay_num, datatype=lay_dt))

    elif tag == "edge":
        for poly in polygons:
            points = [
                [float(p.split(",")[0]), float(p.split(",")[1])]
                for p in poly.split(";")
            ]
            dist = np.sqrt(((points[0][0]) - (points[1][0]))**2 + ((points[0][1]) - (points[1][1]))**2)
            # Adding condition for extremely small edge length
            ## to generate a path to be drawn
            if dist < path_width:
                points[1][0] = points[0][0] + 2 * path_width
            cell.add(gdstk.FlexPath(points, path_width, layer=lay_num, datatype=lay_dt))

    elif "float" or "text" in tag :
        # Known antenna values for antenna ratios
        pass

    else:
        logging.error(f"## Unknown type: {tag} ignored")


def convert_results_db_to_gds(results_database: str, rules_tested: list):
    """
    This function will parse Klayout database for analysis.
    It converts the lyrdb klayout database file to GDSII file

    Parameters
    ----------
    results_database : string or Path object
        Path string to the results file
    rules_tested : list
        List of strings that holds the rule names that are covered by the test case.

    Returns
    -------
    output_gds_path : string or Path
        Path of the output marker gds file generated from db file.
    output_runset_path : string or Path
        Path of the output drc runset used for analysis.
    """

    # Writing analysis rule deck
    pass_marker = "input(2, 222)"
    fail_marker = "input(3, 222)"
    fail_marker2 = "input(6, 222)"
    text_marker = "input(11, 222)"

    output_runset_path = f'{results_database.replace(".lyrdb", "")}_analysis.drc'

    analysis_rules = []
    runset_analysis_setup = f"""
    source($input)
    report("DRC analysis run report at", $report)
    pass_marker = {pass_marker}
    fail_marker = {fail_marker}
    fail_marker2 = {fail_marker2}
    text_marker = {text_marker}

    full_chip = extent.sized(0.0)

    """
    analysis_rules.append(runset_analysis_setup)

    # Generating violated rules and its points
    cell_name = ""
    lib = None
    cell = None
    in_item = False
    rule_data_type_map = list()

    for ev, elem in tqdm(ET.iterparse(results_database, events=("start", "end"))):

        if elem.tag != "item" and not in_item:
            elem.clear()
            continue

        if elem.tag != "item" and in_item:
            continue

        if elem.tag == "item" and ev == "start":
            in_item = True
            continue

        rules = elem.findall("category")
        values = elem.findall("values")

        if len(values) > 0:
            polygons = values[0].findall("value")
        else:
            polygons = []

        if cell_name == "":
            all_cells = elem.findall("cell")

            if len(all_cells) > 0:
                cell_name = all_cells[0].text

                if cell_name is None:
                    elem.clear()
                    continue

                lib = gdstk.Library(f"{cell_name}_markers")
                cell = lib.new_cell(f"{cell_name}_markers")

        if len(rules) > 0:
            rule_name = rules[0].text.replace("'", "")
            if rule_name is None:
                elem.clear()
                continue
        else:
            elem.clear()
            continue

        if rule_name not in rule_data_type_map:
            rule_data_type_map.append(rule_name)

        ## Drawing polygons here.
        rule_lay_dt = rule_data_type_map.index(rule_name) + 1
        if cell is not None:
            for p in polygons:
                draw_polygons(p.text, cell, RULE_LAY_NUM, rule_lay_dt, PATH_WIDTH)

        ## Clearing memeory
        in_item = False
        elem.clear()

    # Writing final marker gds file
    if lib is not None:
        output_gds_path = f'{results_database.replace(".lyrdb", "")}_markers.gds'
        lib.write_gds(output_gds_path)
    else:
        logging.error("Failed to get any results in the lyrdb database.")
        exit(1)

    # Saving analysis rule deck.
    for r in rule_data_type_map:
        rule_lay_dt = rule_data_type_map.index(r) + 1
        rule_layer_name = f'rule_{r.replace(".", "_")}'
        rule_layer = f"{rule_layer_name} = input({RULE_LAY_NUM}, {rule_lay_dt})"

        pass_patterns_rule = f"""
        pass_marker.interacting( text_marker.texts("{r}") ).output("{r}{RULE_STR_SEP}pass_patterns", "{r}{RULE_STR_SEP}pass_patterns polygons")
        """
        fail_patterns_rule = f"""
        fail_marker2.interacting(fail_marker.interacting(text_marker.texts("{r}")) ).or( fail_marker.interacting(text_marker.texts("{r}")).not_interacting(fail_marker2) ).output("{r}{RULE_STR_SEP}fail_patterns", "{r}{RULE_STR_SEP}fail_patterns polygons")
        """
        false_pos_rule = f"""
        pass_marker.interacting(text_marker.texts("{r}")).interacting({rule_layer_name}).output("{r}{RULE_STR_SEP}false_positive", "{r}{RULE_STR_SEP}false_positive occurred")
        """
        false_neg_rule = f"""
        ((fail_marker2.interacting(fail_marker.interacting(text_marker.texts("{r}")))).or((fail_marker.interacting(input(11, 222).texts("{r}")).not_interacting(fail_marker2)))).not_interacting({rule_layer_name}).output("{r}{RULE_STR_SEP}false_negative", "{r}{RULE_STR_SEP}false_negative occurred")
        """
        rule_not_tested = f"""
        full_chip.not_interacting({rule_layer_name}).output("{r}{RULE_STR_SEP}not_tested", "{r}{RULE_STR_SEP}not_tested occurred")
        """

        analysis_rules.append(rule_layer)
        analysis_rules.append(pass_patterns_rule)
        analysis_rules.append(fail_patterns_rule)
        analysis_rules.append(false_pos_rule)
        analysis_rules.append(false_neg_rule)
        analysis_rules.append(rule_not_tested)

    rule_lay_dt = len(rule_data_type_map) + 1

    for r in rules_tested:
        if r in rule_data_type_map:
            continue

        rule_layer_name = f'rule_{r.replace(".", "_")}'
        rule_layer = f"{rule_layer_name} = input({RULE_LAY_NUM}, {rule_lay_dt})"

        pass_patterns_rule = f"""
        pass_marker.interacting( text_marker.texts("{r}") ).output("{r}{RULE_STR_SEP}pass_patterns", "{r}{RULE_STR_SEP}pass_patterns polygons")
        """
        fail_patterns_rule = f"""
        fail_marker2.interacting(fail_marker.interacting(text_marker.texts("{r}")) ).or( fail_marker.interacting(text_marker.texts("{r}")).not_interacting(fail_marker2) ).output("{r}{RULE_STR_SEP}fail_patterns", "{r}{RULE_STR_SEP}fail_patterns polygons")
        """

        false_pos_rule = f"""
        pass_marker.interacting(text_marker.texts("{r}")).interacting({rule_layer_name}).output("{r}{RULE_STR_SEP}false_positive", "{r}{RULE_STR_SEP}false_positive occurred")
        """
        false_neg_rule = f"""
        ((fail_marker2.interacting(fail_marker.interacting(text_marker.texts("{r}")))).or((fail_marker.interacting(input(11, 222).texts("{r}")).not_interacting(fail_marker2)))).not_interacting({rule_layer_name}).output("{r}{RULE_STR_SEP}false_negative", "{r}{RULE_STR_SEP}false_negative occurred")
        """
        rule_not_tested = f"""
        full_chip.not_interacting({rule_layer_name}).output("{r}{RULE_STR_SEP}not_tested", "{r}{RULE_STR_SEP}not_tested occurred")
        """

        analysis_rules.append(rule_layer)
        analysis_rules.append(pass_patterns_rule)
        analysis_rules.append(fail_patterns_rule)
        analysis_rules.append(false_pos_rule)
        analysis_rules.append(false_neg_rule)
        analysis_rules.append(rule_not_tested)

        rule_lay_dt += 1

    with open(output_runset_path, "w") as runset_analysis:
        runset_analysis.write("".join(analysis_rules))

    return output_gds_path, output_runset_path


def build_tests_dataframe(unit_test_cases_dir, target_table):
    """
    This function is used for getting all test cases available in a formated dataframe before running.

    Parameters
    ----------
    unit_test_cases_dir : str
        Path string to the location of unit test cases path.
    target_table : str or None
        Name of table that we want to run regression for. If None, run all found.

    Returns
    -------
    pd.DataFrame
        A DataFrame that has all the targetted test cases that we need to run.
    """
    all_unit_test_cases = sorted(
        Path(unit_test_cases_dir).rglob("*.{}".format(SUPPORTED_TC_EXT))
    )
    logging.info(
        "## Total number of test cases found: {}".format(len(all_unit_test_cases))
    )

    # Get test cases df from test cases
    tc_df = pd.DataFrame({"test_path": all_unit_test_cases})
    tc_df["testcase_basename"] = tc_df["test_path"].apply(lambda x: x.name.replace(".gds", ""))
    tc_df["table_name"] = tc_df["testcase_basename"].apply(lambda x: x.split("-")[0])
    tc_df["test_criteria"] = tc_df["test_path"].apply(lambda x: x.parent.name)

    if target_table is not None:
        tc_df = tc_df[tc_df["table_name"] == target_table]

    if len(tc_df) < 1:
        logging.error("No test cases remaining after filtering.")
        exit(1)

    tc_df["run_id"] = range(len(tc_df))
    return tc_df


def aggregate_results(
    tc_df: pd.DataFrame, results_df: pd.DataFrame, rules_df: pd.DataFrame
):
    """
    aggregate_results Aggregate the results for all runs.

    Parameters
    ----------
    tc_df : pd.DataFrame
        Dataframe that holds the information about the test cases.
    results_df : pd.DataFrame
        Dataframe that holds the information about the unit test rules.
    rules_df : pd.DataFrame
        Dataframe that holds the information about all the rules implemented in the rule deck.

    Returns
    -------
    pd.DataFrame
        A DataFrame that has all data analysis aggregated into one.
    """
    if len(rules_df) < 1 and len(results_df) < 1:
        logging.error("## There are no rules for analysis or run.")
        exit(1)
    elif len(rules_df) < 1 and len(results_df) > 0:
        df = results_df
    elif len(rules_df) > 0 and len(results_df) < 1:
        df = rules_df
        for c in ANALYSIS_RULES:
            df[c] = 0
    else:
        df = results_df.merge(rules_df, how="outer", on=["table_name", "rule_name"])

    df[ANALYSIS_RULES] = df[ANALYSIS_RULES].fillna(0)
    df["in_rule_deck"] = df["in_rule_deck"].fillna(0)
    df = df.merge(tc_df[["table_name", "run_status"]], how="left", on="table_name")

    df["rule_status"] = "Unknown"
    df.loc[(df["false_negative"] > 0), "rule_status"] = "Rule Failed"
    df.loc[(df["false_positive"] > 0), "rule_status"] = "Rule Failed"
    df.loc[
        (df["not_tested"] > 0) | (df["pass_patterns"] < 1), "rule_status"
    ] = "Rule Not Tested"
    df.loc[
        (df["fail_patterns"] < 1) | (df["pass_patterns"] < 1), "rule_status"
    ] = "Rule Not Tested"
    df.loc[(df["in_rule_deck"] < 1), "rule_status"] = "Rule Not Implemented"
    df.loc[
        ~(df["run_status"].isin(["completed"])), "rule_status"
    ] = "Test Case Run Failed"

    df.loc[
        (df["not_tested"] > 0) | (df["pass_patterns"] < 1), "rule_status"
    ] = "Rule Not Tested"

    rule_exp_cond = ((df["fail_patterns"] > 0) & (df["false_negative"] > 0) & (df["not_tested"] > 0))
    df.loc[rule_exp_cond, "rule_status"] = "Rule Syntax Exception"

    pass_cond = (
        (df["pass_patterns"] > 0)
        & (df["fail_patterns"] > 0)
        & (df["false_negative"] < 1)
        & (df["false_positive"] < 1)
        & (df["in_rule_deck"] > 0)
    )

    df.loc[pass_cond, "rule_status"] = "Passed"
    return df


def run_regression(drc_dir, output_path, target_table, cpu_count):
    """
    Running Regression Procedure.

    This function runs the full regression on all test cases.

    Parameters
    ----------
    drc_dir : string
        Path string to the DRC directory where all the DRC files are located.
    output_path : str
        Path string to the location of the output results of the run.
    target_table : string or None
        Name of table that we want to run regression for. If None, run all found.
    cpu_count : int
        Number of cpus to use in running testcases.
    Returns
    -------
    bool
        If all regression passed, it returns true. If any of the rules failed it returns false.
    """

    ## Parse Existing Rules
    rules_df = parse_existing_rules(drc_dir, output_path, target_table)
    logging.info(
        "## Total number of rules found in rule decks: {}".format(len(rules_df))
    )
    logging.info("## Parsed Rules: \n" + str(rules_df))

    ## Get all test cases available in the repo.
    test_cases_path = os.path.join(drc_dir, "testing/testcases")
    unit_test_cases_path = os.path.join(test_cases_path, "unit")
    tc_df = build_tests_dataframe(unit_test_cases_path, target_table)
    logging.info("## Total table gds files found: {}".format(len(tc_df)))
    logging.info("## Found testcases: \n" + str(tc_df))

    ## Run all test cases.
    results_df, tc_df = run_all_test_cases(tc_df, drc_dir, output_path, cpu_count)
    logging.info("## Testcases found results: \n" + str(results_df))
    logging.info("## Updated testcases: \n" + str(tc_df))

    ## Aggregate all dataframes into one
    df = aggregate_results(tc_df, results_df, rules_df)
    df.drop_duplicates(inplace=True)
    logging.info("## Final analysis table: \n" + str(df))

    ## Generate error if there are any missing info or fails.
    df.to_csv(os.path.join(output_path, "all_test_cases_results.csv"), index=False)

    ## Check if there any rules that generated false positive or false negative
    failing_results = df[~df["rule_status"].isin(["Passed"])]
    logging.info("## Failing test cases: \n" + str(failing_results))

    if len(failing_results) > 0:
        logging.error("## Some test cases failed .....")
        return False
    else:
        logging.info("## All testcases passed.")
        return True


def main(drc_dir: str, output_path: str, target_table: str):
    """
    Main Procedure.

    This function is the main execution procedure

    Parameters
    ----------
    drc_dir : str
        Path string to the DRC directory where all the DRC files are located.
    output_path : str
        Path string to the location of the output results of the run.
    target_table : str or None
        Name of table that we want to run regression for. If None, run all found.
    Returns
    -------
    bool
        If all regression passed, it returns true. If any of the rules failed it returns false.
    """

    # No. of threads
    cpu_count = os.cpu_count() if args["--mp"] is None else int(args["--mp"])

    # Pandas printing setup
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("max_colwidth", None)
    pd.set_option("display.width", 1000)

    # info logs for args
    logging.info("## Run folder is: {}".format(run_dir))
    logging.info("## Target Table is: {}".format(target_table))

    # Start of execution time
    t0 = time.time()

    ## Check Klayout version
    check_klayout_version()

    # Calling regression function
    run_status = run_regression(drc_dir, output_path, target_table, cpu_count)

    #  End of execution time
    logging.info("Total execution time {}s".format(time.time() - t0))

    if run_status:
        logging.info("Test completed successfully.")
    else:
        logging.error("Test failed.")
        exit(1)


# ================================================================
# -------------------------- MAIN --------------------------------
# ================================================================


if __name__ == "__main__":

    # docopt reader
    args = docopt(__doc__, version="DRC Regression: 0.2")

    # arguments
    run_dir = args["--run_dir"]
    target_table = args["--table_name"]

    if run_dir is None:
        # logs format
        run_dir = datetime.utcnow().strftime("unit_tests_%Y_%m_%d_%H_%M_%S")

    # Paths of regression dirs
    testing_dir = os.path.dirname(os.path.abspath(__file__))
    drc_dir = os.path.dirname(testing_dir)
    rules_dir = os.path.join(drc_dir, "rule_decks")
    output_path = os.path.join(testing_dir, run_dir)
    run_name = os.path.basename(output_path)

    # Creating output dir
    os.makedirs(output_path, exist_ok=True)

    # logs format
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler(os.path.join(output_path, "{}.log".format(run_name))),
            logging.StreamHandler(),
        ],
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%d-%b-%Y %H:%M:%S",
    )

    # Calling main function
    run_status = main(drc_dir, output_path, target_table)
