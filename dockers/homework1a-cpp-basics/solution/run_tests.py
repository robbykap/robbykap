import json
from byu_pytest_utils import cache, compile_cpp, format_results_for_gradescope, run_exec, test_files, this_folder


@cache
def numbers_divisible_by_bin():
    return compile_cpp('numbers_divisible_by.cpp')


@cache
def collatz_bin():
    return compile_cpp('collatz.cpp')


@cache
def sqrt_bin():
    return compile_cpp('sqrt.cpp')


# Speed up interaction time
# _run_exec = run_exec
# run_exec = lambda *args, **kwargs: _run_exec(*args, **kwargs, read_timeout=0.1)

test_results = {
    'numbers_divisible_by': [
        {
            'name': 'going_up',
            'points': 6,
            'result': run_exec(
                numbers_divisible_by_bin, 1, 10, 3,
                expected_stdio=test_files / 'ndb_going_up.stdout.txt'
            )
        },
        {
            'name': 'going_down',
            'points': 6,
            'result': run_exec(
                numbers_divisible_by_bin, 10, 1, 3,
                expected_stdio=test_files / 'ndb_going_down.stdout.txt'
            )
        },
        {
            'name': 'going_up_includes_bounds',
            'points': 6,
            'result': run_exec(
                numbers_divisible_by_bin, 2, 8, 2,
                expected_stdio=test_files / 'ndb_includes_bounds_going_up.stdout.txt'
            )
        },
        {
            'name': 'going_down_includes_bounds',
            'points': 6,
            'result': run_exec(
                numbers_divisible_by_bin, 16, 8, 4,
                expected_stdio=test_files / 'ndb_includes_bounds_going_down.stdout.txt'
            )
        },
        {
            'name': 'negative_and_zero',
            'points': 6,
            'result': run_exec(
                numbers_divisible_by_bin, -15, 15, 5,
                expected_stdio=test_files / 'ndb_negative_numbers_and_zero.stdout.txt'
            )
        }
    ],
    'collatz': [
        {
            'name': 'starting_at_5',
            'points': 7.5,
            'result': run_exec(
                collatz_bin, 5,
                expected_stdio=test_files / 'collatz_start_5.stdout.txt'
            )
        },
        {
            'name': 'starting_at_8',
            'points': 7.5,
            'result': run_exec(
                collatz_bin, 8,
                expected_stdio=test_files / 'collatz_start_8.stdout.txt'
            )
        },
        {
            'name': 'starting_at_17',
            'points': 7.5,
            'result': run_exec(
                collatz_bin, 17,
                expected_stdio=test_files / 'collatz_start_17.stdout.txt'
            )
        },
        {
            'name': 'starting_at_20',
            'points': 7.5,
            'result': run_exec(
                collatz_bin, 20,
                expected_stdio=test_files / 'collatz_start_20.stdout.txt'
            )
        }
    ],
    'sqrt': [
        {
            'name': 'negative_input',
            'points': 8,
            'result': run_exec(
                sqrt_bin, -4,
                expected_stdio=test_files / 'sqrt_negative.stdout.txt'
            )
        },
        {
            'name': 'int_input',
            'points': 8,
            'result': run_exec(
                sqrt_bin, 9,
                expected_stdio=test_files / 'sqrt_int.stdout.txt'
            )
        },
        {
            'name': 'double_input',
            'points': 8,
            'result': run_exec(
                sqrt_bin, 1.337,
                expected_stdio=test_files / 'sqrt_double.stdout.txt'
            )
        },
        {
            'name': 'sqrt_11',
            'points': 8,
            'result': run_exec(
                sqrt_bin, 11,
                expected_stdio=test_files / 'sqrt_11.stdout.txt'
            )
        },
        {
            'name': 'sqrt_12.25',
            'points': 8,
            'result': run_exec(
                sqrt_bin, 12.25,
                expected_stdio=test_files / 'sqrt_12.25.stdout.txt'
            )
        }
    ]
}

# print(json.dumps(test_results, indent=2))

results = format_results_for_gradescope(test_results)

with open('results.json', 'w') as file:
    json.dump(results, file, indent=2)
