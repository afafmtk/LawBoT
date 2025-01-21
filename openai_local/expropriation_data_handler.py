# expropriation_data_handler.py
from prompts import MAIN_PROMPT, FIELD_PROMPTS

class ExpropriationDataHandler:
    def __init__(self):
        self.main_prompt = MAIN_PROMPT
        self.field_prompts = FIELD_PROMPTS

    def get_main_prompt(self):
        """Returns the main system prompt."""
        return self.main_prompt

    def get_field_prompt(self, field_name):
        """
        Returns the field-specific prompt based on the field name.

        :param field_name: Name of the field (key)
        :return: Field-specific prompt (value) or a default message if the field is not found
        """
        return self.field_prompts.get(field_name, "Field prompt not available.")
