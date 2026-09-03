from flask import Flask, json, request
from flask_cors import CORS, cross_origin

import stock_cutter # local module

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/', methods=['GET'])
@cross_origin()
def get_csp():
	return 'Cutting Stock Problem'

'''
route for receving data for 1D problem 
'''
@app.route('/stocks_1d', methods=['POST'])
@cross_origin()
def post_stocks_1d():
	'''
	expects two params to be present
	child_rolls:
		array of arrays. E.g [ [quantity, width], [quantity, width], ... ]

	parent_rolls:
		array of arrays. E.g [ [quantity, width], [quantity, width], ... ]
	'''
	import stock_cutter_1d

	data = request.json
	print('data: ', data)

	child_rolls = data['child_rolls']
	parent_rolls = data['parent_rolls']

	'''
	it can be
	exactCuts: cut exactly as many as specified by user
	minWaste: cut some items, more than specified, to avoid waste
	'''
	cutStyle = data['cutStyle']

	# output = stock_cutter_1d.StockCutter1D(child_rolls, parent_rolls, cutStyle=cutStyle)
	output = stock_cutter_1d.StockCutter1D(child_rolls, parent_rolls, large_model=False, cutStyle=cutStyle)

	return output



'''
route for 2D
'''
@app.route('/stocks_2d', methods=['POST'])
@cross_origin()
def post_stocks():
	'''
	expects two params to be present
	child_rects:
		array of arrays. Each inner array is like [w, h] i.e. width & height of rectangle

	parent_rects:
		array of arrays. Each inner array is like [w, h] i.e. width & height of rectangle
	'''
	data = request.json
	print('data: ', data)

	child_rects = data['child_rects']
	parent_rects = data['parent_rects']

	output = stock_cutter.StockCutter(child_rects, parent_rects)

	return output



import re
import csv
import io
import urllib.request
import urllib.error

def parse_sheet_id(input_str):
    if not input_str:
        return None
    input_str = input_str.strip()
    # Match full URL like https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', input_str)
    if match:
        return match.group(1)
    # Check if input_str itself is a valid Sheet ID
    if re.match(r'^[a-zA-Z0-9-_]{15,}$', input_str):
        return input_str
    return None

@app.route('/sheets/fetch', methods=['POST'])
@cross_origin()
def fetch_google_sheet():
    data = request.json or {}
    raw_sheet_id = data.get('sheet_id', '')
    sheet_name = data.get('sheet_name', 'Sheet1')
    range_name = data.get('range', '')

    sheet_id = parse_sheet_id(raw_sheet_id)
    if not sheet_id:
        return json.jsonify({
            'status': 'error',
            'error_type': 'invalid_sheet_id',
            'message': 'Invalid Sheet ID or URL. Please provide a valid Google Sheet ID or shareable link.'
        }), 400

    # Build CSV export URL
    encoded_sheet_name = urllib.parse.quote(sheet_name)
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet_name}"
    if range_name:
        encoded_range = urllib.parse.quote(range_name)
        csv_url += f"&range={encoded_range}"

    req = urllib.request.Request(csv_url, headers={'User-Agent': 'PLAX-Optimiser/2.0'})

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return json.jsonify({
                'status': 'error',
                'error_type': 'permission_required',
                'message': 'Permission required. Please ensure the Google Sheet sharing setting is set to "Anyone with the link can view".'
            }), 403
        elif e.code == 404:
            return json.jsonify({
                'status': 'error',
                'error_type': 'sheet_not_accessible',
                'message': 'Sheet not accessible. Please verify the Sheet ID and tab name.'
            }), 404
        else:
            return json.jsonify({
                'status': 'error',
                'error_type': 'sheet_not_accessible',
                'message': f'Google Sheet HTTP error ({e.code}). Please check your URL and tab name.'
            }), 400
    except urllib.error.URLError:
        return json.jsonify({
            'status': 'error',
            'error_type': 'network_unavailable',
            'message': 'Network unavailable. Unable to reach Google Sheets servers. Please check your internet connection.'
        }), 503
    except Exception as e:
        return json.jsonify({
            'status': 'error',
            'error_type': 'sheet_not_accessible',
            'message': 'An unexpected error occurred while fetching the Google Sheet.'
        }), 500

    # Parse CSV content
    try:
        csv_file = io.StringIO(content)
        reader = csv.reader(csv_file)
        rows = list(reader)

        if not rows:
            return json.jsonify({
                'status': 'error',
                'error_type': 'invalid_data_format',
                'message': 'The fetched sheet is empty. Please add data headers and cut specifications.'
            }), 422

        header = [h.strip().lower() for h in rows[0]]

        # Determine column indexes
        w_idx = next((i for i, h in enumerate(header) if 'width' in h or h == 'w'), -1)
        q_idx = next((i for i, h in enumerate(header) if 'quantity' in h or 'qty' in h or h == 'q'), -1)
        h_idx = next((i for i, h in enumerate(header) if 'height' in h or h == 'h'), -1)
        type_idx = next((i for i, h in enumerate(header) if 'type' in h or 'role' in h or 'category' in h), -1)

        if w_idx == -1 or q_idx == -1:
            # Fallback: try positional columns (0: width, 1: qty or 0: width, 1: height, 2: qty)
            if len(header) >= 2:
                w_idx = 0
                q_idx = 1 if len(header) == 2 else len(header) - 1
                if len(header) >= 3:
                    h_idx = 1
            else:
                return json.jsonify({
                    'status': 'error',
                    'error_type': 'invalid_data_format',
                    'message': 'Invalid data format. Sheet must contain "width" and "quantity" headers.'
                }), 422

        child_rolls = []
        parent_rolls = []
        child_rects = []
        parent_rects = []
        parsed_records = []

        data_rows = rows[1:] if (w_idx != -1 and not rows[0][w_idx].replace('.', '', 1).isdigit()) else rows

        for row_idx, r in enumerate(data_rows):
            if not r or not any(cell.strip() for cell in r):
                continue
            try:
                w_val = float(r[w_idx].strip())
                q_val = int(float(r[q_idx].strip()))
                h_val = float(r[h_idx].strip()) if (h_idx != -1 and h_idx < len(r) and r[h_idx].strip()) else None
                row_type = r[type_idx].strip().lower() if (type_idx != -1 and type_idx < len(r)) else 'child'

                record = {
                    'row': row_idx + 1,
                    'width': int(w_val),
                    'quantity': q_val,
                    'height': int(h_val) if h_val is not None else None,
                    'type': row_type
                }
                parsed_records.append(record)

                if 'parent' in row_type or 'stock' in row_type:
                    parent_rolls.append([q_val, int(w_val)])
                    if h_val is not None:
                        parent_rects.append([int(w_val), int(h_val)])
                else:
                    child_rolls.append([q_val, int(w_val)])
                    if h_val is not None:
                        for _ in range(q_val):
                            child_rects.append([int(w_val), int(h_val)])
            except (ValueError, IndexError):
                continue

        if not parsed_records:
            return json.jsonify({
                'status': 'error',
                'error_type': 'invalid_data_format',
                'message': 'Invalid data format. Could not parse valid numeric width and quantity rows.'
            }), 422

        # Default parent roll if none defined in sheet
        if not parent_rolls:
            parent_rolls = [[10, 100]]
        if not parent_rects and h_idx != -1:
            parent_rects = [[84, 72]]

        return json.jsonify({
            'status': 'success',
            'sheet_id': sheet_id,
            'sheet_name': sheet_name,
            'rows_count': len(parsed_records),
            'child_rolls': child_rolls,
            'parent_rolls': parent_rolls,
            'child_rects': child_rects,
            'parent_rects': parent_rects,
            'raw_records': parsed_records,
            'timestamp': str(json.dumps({'time': 'now'}))
        })

    except Exception as e:
        return json.jsonify({
            'status': 'error',
            'error_type': 'invalid_data_format',
            'message': 'Failed to parse Google Sheet data format.'
        }), 422


if __name__ == '__main__':
    # app.run()
	app.run(threaded=True, port=5000)
