

import ruamel.yaml as yaml 
from pathlib import Path
import sys

import typer

class MyYAML(yaml.YAML):
    def __init__(self):
        yaml.YAML.__init__(self)
        self.preserve_quotes = True
        self.explicit_start = True
        self.indent(mapping=2, sequence=2, offset=0)

app = typer.Typer()

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


@app.command()
def parse_yaml_by_tags(
    infile: str = typer.Argument(..., help="Input file"),  
    outfile: str = typer.Argument(..., help="Output file"), 
    include_tags: str = typer.Option("", help="Include tags separated with commas"), 
    exclude_tags: str = typer.Option("", help="Exclude tags separated with commas"),
    force: bool = typer.Option(False, help="Overrite without prompt if exists outfile ")
    ):
    '''
    Parse YAML files by tags
    Read infile and write into outfile only items with include_tags and without exclude_tags
    Examples: 
      parse_yaml_by_tags.py playbook.yaml playbook_out.yaml --include-tags "test , build" --exclude-tags="demo" --force
      parse_yaml_by_tags.py playbook.yaml playbook_out.yaml --exclude-tags="security"
    Predefined tag WITHOUT-TAGS apply for items without any tags
    '''
    inf = Path(infile)
    outf = Path(outfile)
    if outf.is_file() and force == False:
        if query_yes_no(f"File {outfile} exist. Overwrite? [yes/no]","no") == False:
            print("Exitting...")
            exit(1)


    yml = MyYAML()
    data = yml.load(inf)

    include_tags_set = set( [x.strip() for x in include_tags.split(',') if x.strip() != "" ])
    exclude_tags_set = set( [x.strip() for x in exclude_tags.split(',') if x.strip() != "" ])
            
    to_remove = []
    for idx, item in enumerate(data):
        if "tag" in item:
            #if element have exclude tags - remove
            #first prior
            if len(exclude_tags_set.intersection( set(item['tag']))) > 0:
                to_remove.insert(0, idx)
            else:
                #if element dont have include tags - remove
                if len(include_tags_set.intersection( set(item['tag']))) == 0 \
                   and len(include_tags_set) > 0:
                    to_remove.insert(0, idx)
        else:
            #If no tags and have some include tags - remove
            if "WITHOUT-TAGS" not in include_tags_set:
                if len(include_tags_set) > 0:
                    to_remove.insert(0, idx)

    for idx in to_remove:
        del data[idx]    

    yml.dump(data, outf)


if __name__ == "__main__":
    app()

