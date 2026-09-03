import sys
import json
import pytest
from pathlib import Path

# Ensure deployment modules are importable
sys.path.append(str(Path(__file__).parent.parent / "deployment"))

import stock_cutter_1d
import stock_cutter


def test_1d_basic_cutting_problem():
    """1. Basic cutting problem (1D small & large model)."""
    child_rolls = [[3, 30], [2, 72]]
    parent_rolls = [[10, 100]]

    # Small model execution
    res_small_json = stock_cutter_1d.StockCutter1D(
        child_rolls, parent_rolls, output_json=True, large_model=False, cutStyle="exactCuts"
    )
    res_small = json.loads(res_small_json)

    assert res_small["statusName"] == "OPTIMAL"
    assert res_small["numSolutions"] == "1"
    assert res_small["numUniqueSolutions"] == "1"
    assert res_small["numRollsUsed"] == 3

    # Check arrangement and waste
    solutions = res_small["solutions"]
    assert len(solutions) == 3
    # Total parent width = 100
    for waste, cuts in solutions:
        assert pytest.approx(waste + sum(cuts), abs=1e-5) == 100

    # Large model execution
    res_large_json = stock_cutter_1d.StockCutter1D(
        child_rolls, parent_rolls, output_json=True, large_model=True, cutStyle="exactCuts"
    )
    res_large = json.loads(res_large_json)
    assert res_large["statusName"] == "OPTIMAL"
    assert res_large["numRollsUsed"] == 3


def test_1d_multiple_roll_sizes():
    """2. Multiple roll sizes (1D child demands with different widths)."""
    child_rolls = [[3, 25], [12, 21], [7, 26]]
    parent_rolls = [[10, 100]]

    res_json = stock_cutter_1d.StockCutter1D(
        child_rolls, parent_rolls, output_json=True, large_model=False
    )
    res = json.loads(res_json)

    assert res["statusName"] == "OPTIMAL"
    assert res["numRollsUsed"] == 6

    # Verify demand fulfillment
    total_25 = sum(roll[1].count(25) for roll in res["solutions"])
    total_21 = sum(roll[1].count(21) for roll in res["solutions"])
    total_26 = sum(roll[1].count(26) for roll in res["solutions"])

    assert total_25 == 3
    assert total_21 == 12
    assert total_26 == 7


def test_1d_multiple_customer_requirements():
    """3. Multiple customer requirements / diverse order spectrum."""
    child_rolls = [[3, 3], [3, 1], [2, 4], [2, 2]]
    parent_rolls = [[10, 6]]

    res_json = stock_cutter_1d.StockCutter1D(
        child_rolls, parent_rolls, output_json=True, large_model=False
    )
    res = json.loads(res_json)

    assert res["statusName"] == "OPTIMAL"
    assert res["numRollsUsed"] == 4


def test_1d_different_quantities_min_waste():
    """4. Different quantities and cutStyle='minWaste' constraint behavior."""
    child_rolls = [[3, 30], [2, 72]]
    parent_rolls = [[10, 100]]

    res_json = stock_cutter_1d.StockCutter1D(
        child_rolls, parent_rolls, output_json=True, large_model=False, cutStyle="minWaste"
    )
    res = json.loads(res_json)

    assert res["statusName"] == "OPTIMAL"
    assert res["numRollsUsed"] == 3


def test_1d_overwidth_invalid_input_validation():
    """5 & 6. Invalid input validation: small roll width > parent width."""
    child_rolls = [[1, 120]]
    parent_rolls = [[10, 100]]

    # Returns empty list when invalid
    res = stock_cutter_1d.StockCutter1D(
        child_rolls, parent_rolls, output_json=False, large_model=False
    )
    assert res == []


def test_1d_large_input():
    """7. Large input order set."""
    child_rolls = [[6, 25], [12, 21], [7, 26], [3, 23], [8, 33], [2, 15], [2, 34]]
    parent_rolls = [[10, 144]]

    res_json = stock_cutter_1d.StockCutter1D(
        child_rolls, parent_rolls, output_json=True, large_model=False
    )
    res = json.loads(res_json)

    assert res["statusName"] == "OPTIMAL"
    assert res["numRollsUsed"] == 8


def test_1d_integer_input():
    """8. Integer inputs and exact arithmetic behavior."""
    child_rolls = [[5, 10], [5, 20], [2, 50]]
    parent_rolls = [[10, 100]]

    res_json = stock_cutter_1d.StockCutter1D(
        child_rolls, parent_rolls, output_json=True, large_model=False
    )
    res = json.loads(res_json)

    assert res["statusName"] == "OPTIMAL"
    assert res["numRollsUsed"] == 3


def test_1d_existing_example_inputs():
    """9. Existing example inputs from main blocks."""
    child_rolls = [[3, 3], [3, 1], [2, 4], [2, 2]]
    parent_rolls = [[10, 6]]

    raw_rolls = stock_cutter_1d.StockCutter1D(
        child_rolls, parent_rolls, output_json=False, large_model=False
    )
    assert isinstance(raw_rolls, list)
    assert len(raw_rolls) == 4


def test_2d_basic_cutting_problem():
    """10. 2D CP-SAT cutting stock problem."""
    child_rects = [[27, 17], [27, 17], [18, 56]]
    parent_rects = [[84, 72]]

    res_json = stock_cutter.StockCutter(child_rects, parent_rects, output_json=True)
    res = json.loads(res_json)

    assert res["statusName"] == "OPTIMAL"
    assert res["numSolutions"] == "1"
    assert res["numUniqueSolutions"] == "1"

    solutions = res["solutions"]
    assert len(solutions) == 1
    rect_coords = solutions[0]
    assert len(rect_coords) == 3

    # Ensure no overlap and fits within parent sheet (84 x 72)
    for x1, y1, x2, y2 in rect_coords:
        assert 0 <= x1 < x2 <= 84
        assert 0 <= y1 < y2 <= 72
