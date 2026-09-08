import re
from pathlib import Path


IGNORED_DIRECTORIES = {
    "node_modules",
    ".git",
    "dist",
    "build",
    ".next",
    ".venv",
    "venv",
    "__pycache__",
}


class WorkspaceService:

    def extract_keywords(self, prompt: str):
        words = re.findall(
            r"[a-zA-Z0-9_-]+",
            prompt.lower(),
        )

        stop_words = {
            "the",
            "a",
            "an",
            "to",
            "and",
            "or",
            "of",
            "in",
            "on",
            "for",
            "with",
            "from",
            "is",
            "are",
            "this",
            "that",
            "please",
            "add",
            "create",
            "update",
            "change",
            "modify",
            "remove",
            "delete",
        }

        return [
            word
            for word in words
            if word not in stop_words
               and len(word) > 2
        ]

    def score_file(
            self,
            file_path: str,
            keywords,
    ):
        path_lower = file_path.lower()

        filename = Path(
            file_path
        ).stem.lower()

        score = 0

        for keyword in keywords:

            if keyword in path_lower:
                score += 5

            if keyword == filename:
                score += 10

            if keyword in filename:
                score += 7

        return score

    def rank_files(
            self,
            prompt: str,
            files,
            limit: int = 10,
    ):
        keywords = self.extract_keywords(
            prompt
        )

        scored_files = []

        for file_data in files:

            if isinstance(
                    file_data,
                    dict,
            ):
                path = file_data.get(
                    "path",
                    "",
                )
            else:
                path = file_data

            if not path:
                continue

            score = self.score_file(
                path,
                keywords,
            )

            scored_files.append(
                (
                    score,
                    path,
                )
            )

        scored_files.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            path
            for score, path
            in scored_files[:limit]
        ]