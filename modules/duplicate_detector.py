import os
import sys
import re
from difflib import SequenceMatcher

import pandas as pd


# ============================================================
# PROJECT PATH
# ============================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# LOAD DATA PROCESSOR
# ============================================================

from utils.data_processor import load_projects


# ============================================================
# DUPLICATE DETECTOR
# ============================================================

class DuplicateDetector:

    def __init__(self, df):
        self.df = df.copy()

        # Remove completely empty rows
        self.df = self.df.dropna(
            how="all"
        ).reset_index(drop=True)

        self.columns = self.get_columns()

    # --------------------------------------------------------
    # FIND COLUMN
    # --------------------------------------------------------

    def find_column(self, names):

        # Exact match first
        for name in names:

            for column in self.df.columns:

                if str(column).strip().lower() == name.lower():
                    return column

        # Partial match second
        for column in self.df.columns:

            column_name = str(column).strip().lower()

            for name in names:

                if name.lower() in column_name:
                    return column

        return None

    # --------------------------------------------------------
    # DETECT DATASET COLUMNS
    # --------------------------------------------------------

    def get_columns(self):

        return {

            "id": self.find_column([
                "work_id",
                "project_id",
                "workid",
                "projectid",
                "id"
            ]),

            "description": self.find_column([
                "description",
                "work_description",
                "project_description",
                "work_details",
                "project_details",
                "details"
            ]),

            "title": self.find_column([
                "title",
                "work_name",
                "project_name",
                "name"
            ]),

            "district": self.find_column([
                "district",
                "district_name"
            ]),

            "category": self.find_column([
                "work_category",
                "project_category",
                "category",
                "work_type",
                "project_type"
            ]),

            "agency": self.find_column([
                "implementing_agency",
                "agency",
                "execution_agency"
            ]),

            "cost": self.find_column([
                "cost_estimate_lakhs",
                "estimated_cost_lakhs",
                "estimated_cost",
                "project_cost",
                "cost",
                "sanctioned_amount",
                "approved_amount"
            ])
        }

    # --------------------------------------------------------
    # CLEAN TEXT
    # --------------------------------------------------------

    @staticmethod
    def clean_text(value):

        if pd.isna(value):
            return ""

        text = str(value).lower()

        text = re.sub(
            r"[^a-z0-9\s]",
            " ",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # --------------------------------------------------------
    # TEXT SIMILARITY
    # --------------------------------------------------------

    @staticmethod
    def similarity(text1, text2):

        text1 = DuplicateDetector.clean_text(text1)
        text2 = DuplicateDetector.clean_text(text2)

        if not text1 or not text2:
            return 0.0

        return SequenceMatcher(
            None,
            text1,
            text2
        ).ratio()

    # --------------------------------------------------------
    # GET PROJECT TEXT
    # --------------------------------------------------------

    def get_project_text(self, row):

        parts = []

        description_column = self.columns["description"]
        title_column = self.columns["title"]

        if description_column:

            value = row.get(
                description_column,
                ""
            )

            if not pd.isna(value):
                parts.append(str(value))

        if title_column:

            value = row.get(
                title_column,
                ""
            )

            if not pd.isna(value):
                parts.append(str(value))

        return " ".join(parts)

    # --------------------------------------------------------
    # GET VALUE
    # --------------------------------------------------------

    @staticmethod
    def get_value(row, column):

        if not column:
            return ""

        value = row.get(column, "")

        if pd.isna(value):
            return ""

        return DuplicateDetector.clean_text(
            value
        )

    # --------------------------------------------------------
    # COST
    # --------------------------------------------------------

    @staticmethod
    def get_cost(value):

        if pd.isna(value):
            return None

        try:

            value = str(value)

            value = value.replace(
                ",",
                ""
            )

            value = value.replace(
                "₹",
                ""
            )

            value = value.strip()

            match = re.search(
                r"\d+(?:\.\d+)?",
                value
            )

            if match:

                return float(
                    match.group()
                )

        except Exception:
            pass

        return None

    # --------------------------------------------------------
    # CHECK DUPLICATE IDs
    # --------------------------------------------------------

    def duplicate_ids(self):

        column = self.columns["id"]

        result = set()

        if not column:
            return result

        values = (
            self.df[column]
            .astype(str)
            .str.strip()
        )

        duplicates = values[
            values.duplicated(
                keep=False
            )
        ]

        for index in duplicates.index:

            result.add(index)

        return result

    # --------------------------------------------------------
    # COMPARE TWO PROJECTS
    # --------------------------------------------------------

    def compare(self, row1, row2):

        reasons = []

        score = 0

        # ----------------------------------------------------
        # PROJECT TEXT
        # ----------------------------------------------------

        text1 = self.get_project_text(
            row1
        )

        text2 = self.get_project_text(
            row2
        )

        text_score = self.similarity(
            text1,
            text2
        )

        # ----------------------------------------------------
        # DISTRICT
        # ----------------------------------------------------

        district1 = self.get_value(
            row1,
            self.columns["district"]
        )

        district2 = self.get_value(
            row2,
            self.columns["district"]
        )

        same_district = (
            district1 != "" and
            district2 != "" and
            district1 == district2
        )

        # ----------------------------------------------------
        # CATEGORY
        # ----------------------------------------------------

        category1 = self.get_value(
            row1,
            self.columns["category"]
        )

        category2 = self.get_value(
            row2,
            self.columns["category"]
        )

        same_category = (
            category1 != "" and
            category2 != "" and
            category1 == category2
        )

        # ----------------------------------------------------
        # AGENCY
        # ----------------------------------------------------

        agency1 = self.get_value(
            row1,
            self.columns["agency"]
        )

        agency2 = self.get_value(
            row2,
            self.columns["agency"]
        )

        same_agency = (
            agency1 != "" and
            agency2 != "" and
            agency1 == agency2
        )

        # ----------------------------------------------------
        # SIMILARITY SCORE
        # ----------------------------------------------------

        if text_score >= 0.90:

            score += 55

            reasons.append(
                "Project description/title is highly similar."
            )

        elif text_score >= 0.80:

            score += 45

            reasons.append(
                "Project description/title is very similar."
            )

        elif text_score >= 0.70:

            score += 30

            reasons.append(
                "Project description/title is similar."
            )

        # ----------------------------------------------------
        # SAME DISTRICT
        # ----------------------------------------------------

        if same_district:

            score += 15

            reasons.append(
                "Both projects are in the same district."
            )

        # ----------------------------------------------------
        # SAME CATEGORY
        # ----------------------------------------------------

        if same_category:

            score += 15

            reasons.append(
                "Both projects have the same work category."
            )

        # ----------------------------------------------------
        # SAME AGENCY
        # ----------------------------------------------------

        if same_agency:

            score += 10

            reasons.append(
                "Both projects have the same implementing agency."
            )

        # ----------------------------------------------------
        # COST DIFFERENCE
        # ----------------------------------------------------

        cost_difference = None

        cost_column = self.columns["cost"]

        if cost_column:

            cost1 = self.get_cost(
                row1.get(cost_column)
            )

            cost2 = self.get_cost(
                row2.get(cost_column)
            )

            if (
                cost1 is not None and
                cost2 is not None and
                max(cost1, cost2) > 0
            ):

                cost_difference = (
                    abs(cost1 - cost2)
                    / max(cost1, cost2)
                )

                # Similar projects + large cost difference
                if (
                    text_score >= 0.80 and
                    cost_difference >= 0.40
                ):

                    score += 10

                    reasons.append(
                        "Similar projects have significantly different costs."
                    )

        # ----------------------------------------------------
        # FINAL SCORE
        # ----------------------------------------------------

        score = min(
            score,
            100
        )

        # ----------------------------------------------------
        # POSSIBLE DUPLICATE
        # ----------------------------------------------------

        # We need strong text similarity plus at least
        # one supporting field.

        possible_duplicate = (
            text_score >= 0.70
            and (
                same_district
                or same_category
                or same_agency
            )
        )

        return {
            "similarity": round(
                text_score * 100,
                2
            ),
            "score": score,
            "possible_duplicate":
                possible_duplicate,
            "reasons": reasons
        }

    # --------------------------------------------------------
    # RUN DETECTOR
    # --------------------------------------------------------

    def run(self):

        total = len(self.df)

        duplicate_id_indexes = (
            self.duplicate_ids()
        )

        results = []

        # Store best match for every project
        best_matches = {}

        print(
            f"\nComparing {total} projects..."
        )

        # ----------------------------------------------------
        # PAIR COMPARISON
        # ----------------------------------------------------

        for i in range(total):

            row1 = self.df.iloc[i]

            for j in range(
                i + 1,
                total
            ):

                row2 = self.df.iloc[j]

                comparison = self.compare(
                    row1,
                    row2
                )

                if comparison[
                    "possible_duplicate"
                ]:

                    # Project i
                    if (
                        i not in best_matches
                        or
                        comparison["score"]
                        >
                        best_matches[i]["score"]
                    ):

                        best_matches[i] = {
                            "index": j,
                            "score":
                                comparison["score"],
                            "similarity":
                                comparison["similarity"],
                            "reasons":
                                comparison["reasons"]
                        }

                    # Project j
                    if (
                        j not in best_matches
                        or
                        comparison["score"]
                        >
                        best_matches[j]["score"]
                    ):

                        best_matches[j] = {
                            "index": i,
                            "score":
                                comparison["score"],
                            "similarity":
                                comparison["similarity"],
                            "reasons":
                                comparison["reasons"]
                        }

        # ----------------------------------------------------
        # BUILD RESULTS
        # ----------------------------------------------------

        for i in range(total):

            row = self.df.iloc[i]

            score = 0

            flags = []

            reasons = []

            # ------------------------------------------------
            # DUPLICATE ID
            # ------------------------------------------------

            if i in duplicate_id_indexes:

                score = max(
                    score,
                    70
                )

                flags.append(
                    "Duplicate Work ID"
                )

                reasons.append(
                    "The same work/project ID appears more than once."
                )

            # ------------------------------------------------
            # SIMILAR PROJECT
            # ------------------------------------------------

            if i in best_matches:

                match = best_matches[i]

                score = max(
                    score,
                    match["score"]
                )

                flags.append(
                    "Possible Duplicate"
                )

                reasons.extend(
                    match["reasons"]
                )

            # ------------------------------------------------
            # REMOVE DUPLICATE REASONS
            # ------------------------------------------------

            reasons = list(
                dict.fromkeys(
                    reasons
                )
            )

            flags = list(
                dict.fromkeys(
                    flags
                )
            )

            # ------------------------------------------------
            # RISK LEVEL
            # ------------------------------------------------

            if score >= 70:

                risk_level = "HIGH"
                priority = "IMMEDIATE"

            elif score >= 30:

                risk_level = "MEDIUM"
                priority = "REVIEW"

            else:

                risk_level = "LOW"
                priority = "NORMAL"

            # ------------------------------------------------
            # WORK ID
            # ------------------------------------------------

            work_id = "N/A"

            if self.columns["id"]:

                value = row.get(
                    self.columns["id"],
                    ""
                )

                if not pd.isna(value):

                    work_id = str(
                        value
                    )

            # ------------------------------------------------
            # MATCH INDEX
            # ------------------------------------------------

            matching_project = "None"
            similarity = 0

            if i in best_matches:

                match = best_matches[i]

                matching_project = str(
                    match["index"] + 1
                )

                similarity = match[
                    "similarity"
                ]

            # ------------------------------------------------
            # RESULT
            # ------------------------------------------------

            results.append({

                "work_id":
                    work_id,

                "duplicate_risk_score":
                    score,

                "duplicate_risk_level":
                    risk_level,

                "duplicate_flag":
                    ", ".join(flags)
                    if flags
                    else
                    "No duplicate detected",

                "matching_project_row":
                    matching_project,

                "description_similarity":
                    similarity,

                "duplicate_reasons":
                    " | ".join(reasons)
                    if reasons
                    else
                    "No duplicate anomaly detected",

                "inspection_priority":
                    priority
            })

        return pd.DataFrame(
            results
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("          MPLADS DUPLICATE DETECTION ENGINE")
    print("=" * 70)

    try:

        # ----------------------------------------------------
        # LOAD DATA
        # ----------------------------------------------------

        print(
            "\nLoading dataset..."
        )

        df = load_projects()

        if df is None:

            print(
                "ERROR: Dataset could not be loaded."
            )

            return

        if len(df) == 0:

            print(
                "ERROR: Dataset is empty."
            )

            return

        print(
            f"Dataset loaded successfully."
        )

        print(
            f"Total projects: {len(df)}"
        )

        print(
            "\nColumns:"
        )

        for column in df.columns:

            print(
                f"  - {column}"
            )

        # ----------------------------------------------------
        # CREATE DETECTOR
        # ----------------------------------------------------

        detector = DuplicateDetector(
            df
        )

        # ----------------------------------------------------
        # SHOW DETECTED COLUMNS
        # ----------------------------------------------------

        print(
            "\nDetected columns:"
        )

        for name, column in detector.columns.items():

            print(
                f"  {name:15} : {column}"
            )

        # ----------------------------------------------------
        # RUN
        # ----------------------------------------------------

        result = detector.run()

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("             DUPLICATE DETECTION SUMMARY")
        print("=" * 70)

        high = (
            result[
                "duplicate_risk_level"
            ]
            == "HIGH"
        ).sum()

        medium = (
            result[
                "duplicate_risk_level"
            ]
            == "MEDIUM"
        ).sum()

        low = (
            result[
                "duplicate_risk_level"
            ]
            == "LOW"
        ).sum()

        possible = (
            result[
                "duplicate_flag"
            ]
            !=
            "No duplicate detected"
        ).sum()

        print(
            f"HIGH RISK       : {high}"
        )

        print(
            f"MEDIUM RISK     : {medium}"
        )

        print(
            f"LOW RISK        : {low}"
        )

        print(
            f"FLAGGED PROJECTS: {possible}"
        )

        # ----------------------------------------------------
        # SHOW RESULTS
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("             DUPLICATE ANALYSIS RESULTS")
        print("=" * 70)

        display_columns = [
            "work_id",
            "duplicate_risk_score",
            "duplicate_risk_level",
            "duplicate_flag",
            "matching_project_row",
            "description_similarity",
            "inspection_priority"
        ]

        print(
            result[
                display_columns
            ]
            .sort_values(
                "duplicate_risk_score",
                ascending=False
            )
            .head(20)
            .to_string(
                index=False
            )
        )

        # ----------------------------------------------------
        # SHOW DETAILED HIGH-RISK RESULTS
        # ----------------------------------------------------

        high_risk = result[
            result[
                "duplicate_risk_level"
            ]
            == "HIGH"
        ]

        if not high_risk.empty:

            print()
            print("=" * 70)
            print("             HIGH-RISK DETAILS")
            print("=" * 70)

            for _, row in high_risk.head(10).iterrows():

                print()
                print(
                    f"Work ID: {row['work_id']}"
                )

                print(
                    f"Risk Score: "
                    f"{row['duplicate_risk_score']}/100"
                )

                print(
                    f"Risk Level: "
                    f"{row['duplicate_risk_level']}"
                )

                print(
                    f"Matching Project Row: "
                    f"{row['matching_project_row']}"
                )

                print(
                    f"Similarity: "
                    f"{row['description_similarity']}%"
                )

                print(
                    "Reasons:"
                )

                print(
                    row[
                        "duplicate_reasons"
                    ]
                )

                print(
                    f"Inspection Priority: "
                    f"{row['inspection_priority']}"
                )

                print("-" * 70)

        # ----------------------------------------------------
        # SAVE OUTPUT
        # ----------------------------------------------------

        output_path = os.path.join(
            PROJECT_ROOT,
            "data",
            "duplicate_detection_results.csv"
        )

        result.to_csv(
            output_path,
            index=False
        )

        print()
        print(
            "Result file created:"
        )

        print(
            output_path
        )

        # ----------------------------------------------------
        # COMPLETED
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("       DUPLICATE DETECTION COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except Exception as error:

        print()
        print("=" * 70)
        print("ERROR IN DUPLICATE DETECTOR")
        print("=" * 70)

        print(
            str(error)
        )

        print()
        print(
            "Check the traceback below:"
        )

        import traceback

        traceback.print_exc()

    input(
        "\nPress Enter to close..."
    )


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":
    main()