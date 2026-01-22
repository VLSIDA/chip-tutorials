# Globalfoundries 180nm MCU DRC Testing

Explains how to test GF180nm DRC rule decks.

## Folder Structure

```text
📁 testing
 ┣ 📜README.md                       This file to document the regression.
 ┣ 📜run_regression.py               Main regression script used for DRC testing.
 ┣ 📁testcases                       All testcases used in regression.
 ```

## **Prerequisites**
You need the following set of tools installed to be able to run the regression:
- Python 3.6+
- KLayout 0.28.4+

We have tested this using the following setup:
- Python 3.9.12
- KLayout 0.28.5

## **Usage**

```bash
    run_regression.py (--help| -h)
    run_regression.py [--mp=<num>] [--run_name=<run_name>] [--table_name=<table_name>]
```

Example:

```bash
    python3 run_regression.py --table=dualgate --run_name=dualgate_regression
```

### Options

- `--help -h`                           Print this help message.

- `--mp=<num>`                          The number of threads used in run.

- `--run_name=<run_name>`               Select your run name.
    
- `--table_name=<table_name>`           Target specific table.

## **DRC Outputs**

You could find the regression run results at your run directory if you previously specified it through `--run_name=<run_name>`. Default path of run directory is `unit_tests_<date>_<time>` in current directory.

### Folder Structure of regression run results

```text
📁 unit_tests_<date>_<time>
 ┣ 📜 unit_tests_<date>_<time>.log
 ┣ 📜 all_test_cases_results.csv
 ┗ 📜 rule_deck_rules.csv
 ┗ 📁 <table_name>
    ┣ 📜 drc_run_<date>_<time>.log  
    ┣ 📜 <table_name>_drc.log
    ┣ 📜 <table_name>_main_markers_merged_analysis.log
    ┣ 📜 <table_name>.drc                     
    ┣ 📜 <table_name>_main_analysis.drc  
    ┣ 📜 <table_name>_main.lyrdb        
    ┣ 📜 <table_name>_main_markers_merged_final.lyrdb
    ┣ 📜 <table_name>_main_markers.gds  
    ┣ 📜 <table_name>_main_markers_merged.gds
 ```

The result is a database file (`<table_name>_main_markers_merged_final.lyrdb`) contains all violations. 
You could view it on your file using: `klayout <table_name>_main_markers_merged.gds -m <table_name>_main_markers_merged_final.lyrdb`, or you could view it on your gds file via marker browser option in tools menu using klayout GUI as shown below.

![image](https://user-images.githubusercontent.com/91015308/219004873-be7c1e81-7085-4e82-8cd4-8303bc021e13.png)
