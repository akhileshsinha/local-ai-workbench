import json
import re

from transformers import pipeline


class QwenCoderModel:

    MODEL_NAME = "Qwen/Qwen2.5-Coder-7B-Instruct"

    def __init__(self):
        self.pipe = None

    # ============================================================
    # Load model
    # ============================================================

    def load(self):
        print(
            "Loading Qwen2.5-Coder-7B-Instruct..."
        )

        self.pipe = pipeline(
            "text-generation",
            model=self.MODEL_NAME,
            device="mps",
        )

        print(
            "Qwen2.5-Coder-7B-Instruct loaded."
        )

    # ============================================================
    # Existing code-generation response parser
    # ============================================================

    def parse_response(self, response):

        explanation = ""
        code = ""

        if "EXPLANATION:" in response:
            response = response.split(
                "EXPLANATION:",
                1
            )[1]

        if "CODE:" in response:

            explanation_part, code_part = response.split(
                "CODE:",
                1
            )

            explanation = explanation_part.strip()
            code_part = code_part.strip()

            if "```" in code_part:

                parts = code_part.split("```")

                if len(parts) >= 2:

                    code = parts[1]

                    lines = code.splitlines()

                    if (
                            lines
                            and lines[0].strip().lower()
                            in {
                        "javascript",
                        "typescript",
                        "js",
                        "ts",
                        "jsx",
                        "tsx",
                        "python",
                        "java",
                        "kotlin",
                        "json",
                        "css",
                        "html",
                    }
                    ):
                        lines = lines[1:]

                    code = "\n".join(lines).strip()

            else:
                code = code_part

        else:
            explanation = response

        return {
            "explanation": explanation,
            "code": code,
        }

    # ============================================================
    # Existing single-file code generation
    # ============================================================

    def generate(self, prompt):

        if self.pipe is None:
            self.load()

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert software engineer. "
                    "Analyze the user's request and provide "
                    "a production-quality solution.\n\n"

                    "Your response MUST follow this format:\n\n"

                    "EXPLANATION:\n"
                    "<brief explanation>\n\n"

                    "CODE:\n"
                    "```language\n"
                    "<complete code>\n"
                    "```\n\n"

                    "Do not put anything after the CODE section."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        prompt_text = (
            self.pipe.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        )

        result = self.pipe(
            prompt_text,
            max_new_tokens=2048,
            do_sample=False,
        )

        generated = result[0]["generated_text"]

        response = generated[
            len(prompt_text):
        ].strip()

        return self.parse_response(response)

    # ============================================================
    # Project / Agent generation
    # ============================================================

    def generate_project(
            self,
            prompt,
            workspace_files=None,
    ):

        if self.pipe is None:
            self.load()

        if workspace_files is None:
            workspace_files = []

        # ------------------------------------------------------------
        # Select the most relevant files for the user's request
        # ------------------------------------------------------------

        from services.workspace_service import WorkspaceService

        workspace_service = WorkspaceService()

        relevant_paths = workspace_service.rank_files(
            prompt,
            workspace_files,
            limit=10,
        )

        all_paths = [
            file_data["path"]
            for file_data in workspace_files
        ]

        relevant_path_set = set(relevant_paths)

        unloaded_paths = [
            path
            for path in all_paths
            if path not in relevant_path_set
        ]

        relevant_files = [
            file_data
            for file_data in workspace_files
            if file_data.get("path") in relevant_path_set
        ]

        # ------------------------------------------------------------
        # Build context from relevant files
        # ------------------------------------------------------------

        workspace_context = "\n\n".join(
            f"""
        FILE: {file_data["path"]}

        CONTENT:
        {file_data["content"]}
        """.strip()
            for file_data in relevant_files
        )

        if not workspace_context:
            workspace_context = (
                "(Workspace is empty or no relevant files were found.)"
            )

        # ------------------------------------------------------------
        # Build model messages
        # ------------------------------------------------------------

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert software architect "
                    "and autonomous coding agent.\n\n"

                    "Your job is to analyze the user's request "
                    "and produce a precise set of file operations "
                    "for the existing software workspace.\n\n"

                    "You have access to relevant existing files "
                    "from the workspace, including their actual "
                    "contents.\n\n"

                    "You MUST return ONLY valid JSON.\n"
                    "Do NOT use Markdown.\n"
                    "Do NOT wrap the JSON in ```json fences.\n\n"

                    "The JSON MUST have exactly this structure:\n\n"

                    "{\n"
                    '  "message": "short explanation",\n'
                    '  "actions": [\n'
                    "    {\n"
                    '      "type": "create_file",\n'
                    '      "path": "relative/path/to/file",\n'
                    '      "content": "complete file content"\n'
                    "    },\n"
                    "    {\n"
                    '      "type": "modify_file",\n'
                    '      "path": "relative/path/to/file",\n'
                    '      "content": "complete new file content"\n'
                    "    },\n"
                    "    {\n"
                    '      "type": "delete_file",\n'
                    '      "path": "relative/path/to/file"\n'
                    "    }\n"
                    "  ]\n"
                    "}\n\n"

                    "ACTION RULES:\n"
                    "1. Use only relative file paths.\n"
                    "2. Never use absolute paths.\n"
                    "3. Use forward slashes in paths.\n"
                    "4. Use create_file only when the file does not already exist.\n"
                    "5. Use modify_file when an existing file must be changed.\n"
                    "6. For modify_file, return the COMPLETE new content of the file, not a patch.\n"
                    "7. Use delete_file only when the user request requires removing a file.\n"
                    "8. Do not delete files unnecessarily.\n"
                    "9. Include all important files required to complete the user's request.\n"
                    "10. Do not create unnecessary files.\n"
                    "11. Do not execute commands yourself.\n"
                    "12. Do not describe commands instead of creating the required file actions.\n"
                    "13. Preserve existing project structure whenever possible.\n"
                    "14. Do not overwrite an existing file with create_file.\n"
                    "15. Always return complete file contents for create_file and modify_file.\n"
                    "16. Return an empty actions array if no file changes are required.\n"
                    "17. The output must be valid JSON.\n"
                    "18. Before modifying a file, use its actual content from the workspace.\n"
                    "19. Never invent existing file contents when the file is provided.\n"
                    "20. For modify_file, preserve unrelated existing code.\n"
                    "21. Make the smallest reasonable change required by the user request.\n"
                    "22. Never use create_file for a file listed in the existing workspace.\n"
                    "23. Never use modify_file for a file that does not exist.\n\n"

                    "RELEVANT EXISTING FILES:\n"
                    f"{workspace_context}\n\n"

                    "OTHER EXISTING WORKSPACE FILES:\n"
                    f"{chr(10).join(unloaded_paths)}\n"
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        # ------------------------------------------------------------
        # Generate response
        # ------------------------------------------------------------

        prompt_text = (
            self.pipe.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        )

        result = self.pipe(
            prompt_text,
            max_new_tokens=4096,
            do_sample=False,
        )

        generated = result[0]["generated_text"]

        response = generated[
            len(prompt_text):
        ].strip()

        return self.parse_project_response(
            response
        )

    # ============================================================
    # Project response parser
    # ============================================================

    def parse_project_response(
            self,
            response,
    ):

        cleaned = response.strip()

        # --------------------------------------------------------
        # Remove accidental Markdown JSON fences
        # --------------------------------------------------------

        if cleaned.startswith("```"):

            cleaned = re.sub(
                r"^```(?:json)?\s*",
                "",
                cleaned,
                flags=re.IGNORECASE,
            )

            cleaned = re.sub(
                r"\s*```$",
                "",
                cleaned,
            )

        cleaned = cleaned.strip()

        # --------------------------------------------------------
        # Direct JSON parsing
        # --------------------------------------------------------

        try:

            data = json.loads(cleaned)

        except json.JSONDecodeError:

            # ----------------------------------------------------
            # Try extracting JSON object
            # ----------------------------------------------------

            start = cleaned.find("{")
            end = cleaned.rfind("}")

            if start == -1 or end == -1:

                raise ValueError(
                    "Qwen did not return valid project JSON."
                )

            json_text = cleaned[
                start:end + 1
            ]

            try:

                data = json.loads(
                    json_text
                )

            except json.JSONDecodeError as error:

                raise ValueError(
                    "Unable to parse Qwen project response "
                    f"as JSON: {error}"
                )

        # --------------------------------------------------------
        # Validate top-level structure
        # --------------------------------------------------------

        if not isinstance(data, dict):

            raise ValueError(
                "Project response must be a JSON object."
            )

        message = data.get(
            "message",
            "",
        )

        actions = data.get(
            "actions",
            [],
        )

        if not isinstance(actions, list):

            raise ValueError(
                "Project actions must be an array."
            )

        # --------------------------------------------------------
        # Validate individual actions
        # --------------------------------------------------------

        validated_actions = []

        for action in actions:

            if not isinstance(
                    action,
                    dict,
            ):
                continue

            action_type = action.get(
                "type"
            )

            path = action.get(
                "path"
            )

            content = action.get(
                "content",
                "",
            )

            # ----------------------------------------------------
            # CREATE FILE
            # ----------------------------------------------------

            if action_type == "create_file":

                if not path:
                    continue

                if not isinstance(
                        content,
                        str,
                ):
                    content = str(
                        content
                    )

                validated_actions.append({
                    "type": "create_file",
                    "path": path,
                    "content": content,
                })

            # ----------------------------------------------------
            # MODIFY FILE
            # ----------------------------------------------------

            elif action_type == "modify_file":

                if not path:
                    continue

                if not isinstance(
                        content,
                        str,
                ):
                    content = str(
                        content
                    )

                validated_actions.append({
                    "type": "modify_file",
                    "path": path,
                    "content": content,
                })

            # ----------------------------------------------------
            # DELETE FILE
            # ----------------------------------------------------

            elif action_type == "delete_file":

                if not path:
                    continue

                validated_actions.append({
                    "type": "delete_file",
                    "path": path,
                })

        # --------------------------------------------------------
        # Return normalized project response
        # --------------------------------------------------------

        return {
            "message": message,
            "actions": validated_actions,
        }

    # ============================================================
    # Unload model
    # ============================================================

    def unload(self):

        if self.pipe is None:
            return

        print(
            "Unloading Qwen2.5-Coder-7B-Instruct..."
        )

        del self.pipe

        self.pipe = None
