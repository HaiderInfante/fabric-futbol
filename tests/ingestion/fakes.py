"""Dobles de prueba compartidos por los tests de ingesta."""


class InMemoryWriter:
    """Writer con la misma semántica que bronze_io: solo añade versiones nuevas por clave."""

    def __init__(self):
        self.files = []
        self.tables: dict[str, list[dict]] = {}
        self.manifest: dict[str, str] = {}
        self.manifest_writes = 0

    def write_files(self, files):
        self.files.extend(files)
        return len(files)

    def append(self, table, rows):
        existing = self.tables.setdefault(table, [])
        latest = {r["record_key"]: r["record_hash"] for r in existing}
        new = [r for r in rows if latest.get(r["record_key"]) != r["record_hash"]]
        existing.extend(new)
        return len(new)

    def read_manifest(self, source):
        return dict(self.manifest)

    def write_manifest(self, source, updates, batch_id):
        self.manifest_writes += 1
        self.manifest.update(dict(updates))

    def latest_records(self, table):
        latest = {}
        for row in self.tables.get(table, []):
            latest[row["record_key"]] = row  # filas en orden de inserción: gana la última
        return [
            {k: r[k] for k in ("record_key", "record_context", "payload")} for r in latest.values()
        ]

    def existing_keys(self, table):
        return {r["record_key"] for r in self.tables.get(table, [])}
