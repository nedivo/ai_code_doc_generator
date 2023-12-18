import re


class MDXFormatter:
    def remove_trailing_backticks(self, input_string):
        return input_string.rstrip('`')
    
    def remove_leading_mdx(self, input_string):
        return re.sub(r'^```mdx', '', input_string)
    
    def remove_leading_and_trailing_whitespace(self, input_string):
        return input_string.strip()

    def format_to_mdx(self, documentation):
        if documentation and isinstance(documentation, list):
            documentation = documentation[0]
        else:
            documentation = "No documentation generated."
        
        formatted_documentation = documentation.replace("\\n", "\n")
        formatted_documentation = self.remove_leading_mdx(formatted_documentation)
        formatted_documentation = self.remove_trailing_backticks(formatted_documentation)
        formatted_documentation = self.remove_leading_and_trailing_whitespace(formatted_documentation)
        mdx_content = formatted_documentation
        return mdx_content

    def save_to_mdx_file(self, mdx_content, file_path):
        with open(file_path, 'w') as mdx_file:
            mdx_file.write(mdx_content)