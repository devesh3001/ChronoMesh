"""Read-only, reproducible audit of the supplied practice dataset (stdlib only)."""
import collections
import datetime as dt
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def audit():
    archive = ROOT / "customer_360_dataset.zip"
    report = {"archive_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(), "scenarios": []}
    all_ids = []
    live_ids = []
    with zipfile.ZipFile(archive) as z:
        scenarios = sorted({n.split('/')[0] for n in z.namelist() if n.endswith('/live_stream.jsonl')})
        for scenario in scenarios:
            entity = json.loads(z.read(f"{scenario}/entities.json"))
            truth = json.loads(z.read(f"{scenario}/ground_truth.json"))
            item = {"directory": scenario, "label_scenario_id": truth['scenario_id'],
                    "checkpoints": len(truth['checkpoints']), "streams": {}}
            accounts = {a['account_id'] for a in entity['accounts']}
            for name in ['history_seed', 'live_stream']:
                rows = [json.loads(l) for l in z.read(f"{scenario}/{name}.jsonl").decode().splitlines() if l.strip()]
                all_ids.extend(r['event_id'] for r in rows)
                if name == 'live_stream':
                    live_ids.extend(r['event_id'] for r in rows)
                late = []
                for r in rows:
                    delay = (dt.datetime.fromisoformat(r['ingestion_time']) - dt.datetime.fromisoformat(r['event_time'])).total_seconds()
                    if delay:
                        late.append({"event_id": r['event_id'], "delay_seconds": delay})
                item['streams'][name] = {
                    'rows': len(rows), 'types': dict(collections.Counter(r['event_type'] for r in rows)),
                    'first_event_time': min(r['event_time'] for r in rows),
                    'last_event_time': max(r['event_time'] for r in rows),
                    'duplicate_ids_within_file': len(rows) - len({r['event_id'] for r in rows}),
                    'event_time_order_inversions': sum(a['event_time'] > b['event_time'] for a, b in zip(rows, rows[1:])),
                    'ingestion_time_order_inversions': sum(a['ingestion_time'] > b['ingestion_time'] for a, b in zip(rows, rows[1:])),
                    'customer_mismatches': sum(r['customer_id'] != entity['customer_id'] for r in rows),
                    'account_mismatches': sum(r['account_id'] is not None and r['account_id'] not in accounts for r in rows),
                    'late_events': late,
                }
            report['scenarios'].append(item)
    report['total_rows'] = len(all_ids)
    report['duplicate_id_occurrences_across_all_files'] = len(all_ids) - len(set(all_ids))
    report['duplicate_id_occurrences_across_live_files'] = len(live_ids) - len(set(live_ids))
    report['scope_note'] = 'Practice labels were inspected for requirements analysis. They must never be available to inference workers.'
    return report


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
