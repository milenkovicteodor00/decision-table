import csv
from pathlib import Path
from typing import List, Dict, Any, Tuple
from app.models.abstract import AbstractDecisionTable
from app.models.decision_data_holder import DecisionDataHolder


class DecisionTable(AbstractDecisionTable):
    def __init__(self, rules: List[Dict[str, Any]]):
        """
        Initialize DecisionTable with parsed rules.

        Args:
            rules: List of dictionaries containing input conditions and output values
        """
        self.rules = rules

    @staticmethod
    def create_from_csv(filepath: Path) -> "DecisionTable":
        """
        Create a DecisionTable instance from a CSV file.

        Args:
            filepath: Path to the CSV file containing decision rules

        Returns:
            DecisionTable instance
        """
        rules = []

        with open(filepath, "r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=";")
            headers = next(reader)

            # Find the separator column (marked with '*')
            separator_index = headers.index("*")
            input_columns = headers[:separator_index]
            output_columns = headers[separator_index + 1 :]

            for row in reader:
                if not row or all(cell.strip() == "" for cell in row):
                    continue

                rule = {"input_conditions": {}, "output_values": {}}

                # Parse input conditions
                for i, column in enumerate(input_columns):
                    condition = row[i].strip()
                    if condition:
                        rule["input_conditions"][column] = condition

                # Parse output values
                for i, column in enumerate(output_columns):
                    value = row[separator_index + 1 + i].strip()
                    if value:
                        # Remove quotes from output values
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        rule["output_values"][column] = value

                rules.append(rule)

        return DecisionTable(rules)

    def evaluate(self, ddh: DecisionDataHolder) -> bool:
        """
        Evaluate the decision table against the provided data.

        Args:
            ddh: DecisionDataHolder containing input values

        Returns:
            True if a matching rule was found and outputs were set, False otherwise
        """
        for rule in self.rules:
            if self._check_conditions(rule["input_conditions"], ddh):
                # Apply output values
                for output_key, output_value in rule["output_values"].items():
                    ddh[output_key] = output_value
                return True

        return False

    def _check_conditions(self, conditions: Dict[str, str], ddh: DecisionDataHolder) -> bool:
        """
        Check if all input conditions are satisfied.

        Args:
            conditions: Dictionary of column names to condition strings
            ddh: DecisionDataHolder containing input values

        Returns:
            True if all conditions are met, False otherwise
        """
        for column, condition in conditions.items():
            if not self._evaluate_condition(column, condition, ddh):
                return False
        return True

    def _evaluate_condition(self, column: str, condition: str, ddh: DecisionDataHolder) -> bool:
        """
        Evaluate a single condition.

        Args:
            column: Column name
            condition: Condition string (e.g., "=false", ">10", "<=10")
            ddh: DecisionDataHolder containing input values

        Returns:
            True if condition is met, False otherwise
        """
        if column not in ddh:
            return False

        value = ddh[column]

        # Handle equality conditions
        if condition.startswith("="):
            expected_value = condition[1:]
            # Convert string representations to appropriate types
            if expected_value.lower() == "true":
                return value is True
            elif expected_value.lower() == "false":
                return value is False
            else:
                # Try to convert to number for numeric comparison
                try:
                    expected_numeric = float(expected_value)
                    return float(value) == expected_numeric
                except (ValueError, TypeError):
                    return str(value) == expected_value

        # Handle comparison conditions
        elif condition.startswith(">"):
            try:
                threshold = float(condition[1:])
                return float(value) > threshold
            except (ValueError, TypeError):
                return False

        elif condition.startswith("<"):
            try:
                threshold = float(condition[1:])
                return float(value) < threshold
            except (ValueError, TypeError):
                return False

        elif condition.startswith(">="):
            try:
                threshold = float(condition[2:])
                return float(value) >= threshold
            except (ValueError, TypeError):
                return False

        elif condition.startswith("<="):
            try:
                threshold = float(condition[2:])
                return float(value) <= threshold
            except (ValueError, TypeError):
                return False

        # Handle not equal conditions
        elif condition.startswith("!="):
            expected_value = condition[2:]
            if expected_value.lower() == "true":
                return value is not True
            elif expected_value.lower() == "false":
                return value is not False
            else:
                try:
                    expected_numeric = float(expected_value)
                    return float(value) != expected_numeric
                except (ValueError, TypeError):
                    return str(value) != expected_value

        return False
