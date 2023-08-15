from typing import Union, List
import subprocess
import os


def identify_type(variable: Union[List[List[str]], List[str], str, List[List[int]], List[int], int]) -> str:
    """
    Identify the type of the given variable.

    This function determines the type of the input variable, which can be one of the following:
    - str
    - int
    - List[str]
    - List[int]
    - List[List[str]]
    - List[List[int]]

    Parameters:
    - variable (Union[List[List[str]], List[str], str, List[List[int]], List[int], int]): The variable whose type needs to be identified.

    Returns:
    - str: A string description of the variable's type. The possible return values are:
      - "str"
      - "int"
      - "list[str]"
      - "list[int]"
      - "list[list[str]]"
      - "list[list[int]]"
      If the type does not match any of the above, it returns "unknown".

    Examples:
    >>> identify_type("Hello")
    'str'

    >>> identify_type([1, 2, 3])
    'list[int]'

    >>> identify_type([["Hello", "World"], ["Hi", "There"]])
    'list[list[str]]'

    >>> identify_type([[1, 2], [3, 4]])
    'list[list[int]]'
    """
    if isinstance(variable, str):
        return "str"
    elif isinstance(variable, int):
        return "int"
    elif isinstance(variable, list):
        if all(isinstance(item, str) for item in variable):
            return "list[str]"
        elif all(isinstance(item, int) for item in variable):
            return "list[int]"
        elif all(isinstance(item, list) for item in variable) and all(isinstance(sub_item, str) for item in variable for sub_item in item):
            return "list[list[str]]"
        elif all(isinstance(item, list) for item in variable) and all(isinstance(sub_item, int) for item in variable for sub_item in item):
            return "list[list[int]]"
    return "unknown"


class LCM:
    """
    This class provides functionalities to work with the LCM algorithm for frequent pattern mining.
    LCM accepts only interger transactions. LCM provides only a perl wrapper. This class accepts string transactions.

    Files named lcm.dat and lcm.out are made for debugging.

    Attributes:
        prog (str): Path to the LCM program.
        transaction (list): List of transactions.
        transactionfile (str): File name to save transactions.
        outputfile (str): File name to save LCM output.

    An example:

    import pandas as pd

    transactions = [
        ["apple", "banana", "cherry"],
        ["apple", "banana"],
        ["apple", "grape"],
        ["banana", "cherry"],
        ["apple", "banana", "grape"],
        ["cherry"],
        ["banana", "grape"],
        ["apple", "grape"],
        ["apple", "banana", "cherry", "grape"],
        ["apple", "banana", "grape"]
    ]
    lcm = LCM("lcm53/lcm",transactions)

    # freqnency mining
    lcm.run()
    print(pd.DataFrame(lcm.read()))

    # freqnency mining
    lcm.run(target="cherry")
    print(pd.DataFrame(lcm.read()))

    # rule mining
    lcm.run(rule_for_item="banana")
    print(pd.DataFrame(lcm.read()))
    """

    def __init__(self, prog: str, transaction: list, transactionfile: str = "lcm.dat", outputfile: str = "lcm.out"):
        """
        Initializes LCM with program path, transactions, and file names for saving.

        This function examines only the existence of the file 'prog'.

        Args:
            prog (str): Path to the LCM program.
            transaction (list): List of transactions.
            transactionfile (str, optional): File name to save transactions. Defaults to "lcm.dat".
            outputfile (str, optional): File name to save LCM output. Defaults to "lcm.out".
        """
        self.prog = prog
        if not os.path.exists(prog):
            print("program aborted in LCM class.")
            print("faild to find the program {}.".format(prog))
            print("check the existence of the program {}.".format(prog))
            print("You can find lcm at http://research.nii.ac.jp/~uno/codes-j.htm")
            raise RuntimeError(f"Failed to find the program {prog}. Check its existence.")

        self.transaction = transaction
        self.transactionfile = transactionfile
        self.outputfile = outputfile

        # print("transaction length=", len(transaction))
        self.transform_transaction(self.transaction)

    def transform_transaction(self, transaction: List[List[str]], start_from1=False) -> list:
        """
        Transforms string transactions into numerical transactions.

        Args:
            transaction (list): List of transactions.

        Returns:
            list: List of transformed transactions.
        """
        type_ = identify_type(transaction)
        if type_ != "list[list[str]]":
            raise RuntimeError("Error in transform_transaction. unknown type {type_} for transaction.")
        # make itemlist
        itemlist = []
        for x in transaction:
            itemlist.extend(x)
        itemlist = list(set(itemlist))
        self.itemlist = itemlist
        # 双方向dicの作成
        item_name2id = {}
        item_id2name = {}
        if start_from1:
            for i, x in enumerate(itemlist):
                item_name2id[x] = i + 1
                item_id2name[str(i + 1)] = x
        else:
            for i, x in enumerate(itemlist):
                item_name2id[x] = i
                item_id2name[str(i)] = x
        self.item_name2id = item_name2id
        self.item_id2name = item_id2name
        # print(item_id2name)
        # 文字列transactionを数字transactionに変換
        transaction2 = []
        for items in transaction:
            line = []
            for x in items:
                line.append(item_name2id[x])
            # line = list(map(str,line))
            transaction2.append(line)
        self.transaction_transformed = transaction2
        return transaction2

    def transform_items(self, items: Union[List[str], str]) -> list:
        """
        Transforms a list or string of items into numerical format.

        Args:
            items (list or str): List or string of items to be transformed.

        Returns:
            List[int] or int: Transformed items in numerical format.
        """
        type_ = identify_type(items)
        if type_ == "list[str]":
            itemsout = []
            for x in items:
                itemsout.append(self.item_name2id[x])
        elif type_ == "str":
            itemsout = self.item_name2id[items]
        else:
            raise RuntimeError("Error in transform_items. unknown type {type_} for transaction.")

        return itemsout

    def inverse_transform_items(self, items: Union[List[str], str]) -> list:
        """
        Inverse transforms a list or string of items from numerical back to their original format.

        Args:
            items (list or str): List or string of items in numerical format to be inverse transformed.

        Returns:
            List[str] or str: Original format of items.
        """
        type_ = identify_type(items)
        if type_ == "list[str]":
            itemsout = []
            for x in items:
                itemsout.append(self.item_id2name[x])
        elif type_ == "str":
            itemsout = self.item_id2name[items]
        else:
            raise TypeError(f"Error in inverse_transform_items: unknown type {type_}")
        return itemsout

    def inverse_transform_transaction(self, items: Union[list, str]) -> list:
        return self.inverse_transform_itemslist(items)

    def inverse_transform_itemslist(self, itemslist: List[List[str]]) -> list:
        """
        Inverse transforms a list of items lists from numerical back to their original format.

        Args:
            itemslist (List[List[str]]): List of items lists in numerical format to be inverse transformed.

        Returns:
            List[str] or List[List[str]]: Original format of items lists.
        """
        # print("inverse_transform_itemslist", itemslist)
        type_ = identify_type(itemslist)
        if type_ not in ["list[list[str]]"]: #, "list[list[int]]"]:
            raise TypeError(f"Error in inverse_transform_itemslist: unknown type {type_}")
        rulelist2 = []
        for rule in itemslist:
            rule2 = self.inverse_transform_items(rule)
            rulelist2.append(rule2)
        return rulelist2

    def write_transaction(self, targetid: Union[str, None] = None):
        """
        Writes the transformed transactions to a file. 

        If a target ID is provided, only transactions containing that ID will be written. 
        Otherwise, all transformed transactions will be saved.

        Parameters:
        - targetid (int, optional): The ID of the target item. If provided, only transactions 
                                    containing this ID will be saved. Default is None.

        Attributes Used:
        - self.transactionfile (str): Path to the output file where transactions are saved.
        - self.transaction_transformed (list of list): Transformed transactions to be written to the file.

        Side Effects:
        - Writes the transactions to the file specified by self.transactionfile.
        - Prints a message indicating that the file was created.
        """
        with open(self.transactionfile, "w") as f:
            for x in self.transaction_transformed:
                if targetid is None:
                    y = " ".join(list(map(str, x)))
                    f.write(y + "\n")
                else:
                    if targetid in x:
                        y = " ".join(list(map(str, x)))
                        f.write(y + "\n")
            print(f"{self.transactionfile} is made.")

    def run(self, min_support: int = 1, itemset_mining: str = "closed_frequent",
            rule_for_item: Union[str, None] = None, target: Union[str, None] = None,
            option: dict = {}) -> int:
        """
        Executes the LCM program with the specified parameters.

        If rule_for_item has a value, save all the transactions to a file and perform rule mining.
        If the target has a value, limit to transactions that include the target, save to file, and then perform frequency mining. The total number of transactions is different from the original number of transactions.
        If both the value of target and rule_for_item are None, save all the transactions to a file, then frequency minig is performed for the whole.

        Args:
            min_support (int, optional): Minimum support threshold. Defaults to 1.
            itemset_mining (str, optional): Mining type, one of "frequent", "closed_frequent", "maximal_frequent", "positive-closed". Defaults to "closed_frequent".
            rule_for_item (str or None, optional): Specific item to find rules for. Defaults to None.
            target (str or None, optional): Specific target to mine. Defaults to None.
            option (dict, optional): Additional LCM command options. Defaults to empty dictionary.

        Returns:
            int: Return code from the subprocess call to the LCM program.
        """
        itemset_mining_dic = {"frequent": "F", "closed_frequent": "C", "maximal_frequent": "M",
                              "positive-closed": "P"}

        self.min_support = min_support

        self.itemset_mining = itemset_mining

        self.rule_for_item = rule_for_item
        self.target = target

        # option_default = {"min_confidence": 0.5, "min_itemset_size": 1}  # ,"output_num_most_frequent_items":100}
        # option_default.update(option)
        OPTION_DEFAULT = {"min_confidence": 0.5, "min_itemset_size": 1}  # , "output_num_most_frequent_items":100}
        option = {**OPTION_DEFAULT, **option}

        optadd = []

        if rule_for_item is not None and target is not None:
            raise RuntimeError("don't add both rule_for_item and target")

        if rule_for_item is not None and target is None:
            # rule mining
            opt = f"{itemset_mining_dic[itemset_mining]}fRs"

            if option:

                if "min_confidence" in option:
                    optadd = [f"-a {option['min_confidence']}"]
                if "max_confidence" in option:
                    optadd = [f"-A {option['max_confidence']}"]
                if "min_itemset_size" in option:
                    optadd.append(f"-l {option['min_itemset_size']}")
                if "max_itemset_size" in option:
                    optadd.append(f"-u {option['max_itemset_size']}")

            if len(rule_for_item) > 0:
                targetid = self.transform_items(rule_for_item)
                optadd.append("-i {}".format(targetid))

            self.write_transaction()

        if rule_for_item is None and target is not None:
            # frequency mining
            opt = f"{itemset_mining_dic[itemset_mining]}fs"

            targetid = self.transform_items(target)
            if option:

                if "min_itemset_size" in option:
                    optadd.append(f"-l {option['min_itemset_size']}")
                if "max_itemset_size" in option:
                    optadd.append(f"-u {option['max_itemset_size']}")

                # if "output_num_most_frequent_items" in option:
                #    optadd.append( "-K {}".format(option["output_num_most_frequent_items"]) )
            self.write_transaction(targetid)

        if target is None and rule_for_item is None:
            # frequency mining for any
            opt = f"{itemset_mining_dic[itemset_mining]}Rfs"
            if option:

                if "min_itemset_size" in option:
                    optadd.append(f"-l {option['min_itemset_size']}")
                if "max_itemset_size" in option:
                    optadd.append(f"-u {option['max_itemset_size']}")

            self.write_transaction()

        if False:
            cmd = f"{self.prog} {opt} {' '.join(optadd)} {self.transactionfile} {self.min_support} {self.outputfile}"
            print("command", cmd)
            proc = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            # Break down cmd into a list
            cmd_list = [self.prog, opt]
            # Extend the list with the options from optadd
            cmd_list.extend(" ".join(optadd).split())
            # Add the remaining parameters
            cmd_list.extend([self.transactionfile, str(self.min_support), self.outputfile])
            print(" ".join(cmd_list))
            # Now, you can call subprocess with this list:
            proc = subprocess.call(cmd_list, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print("return code", proc)
        return proc

    def read_lines(self) -> list:
        """
        Reads lines from the output file of the LCM program.

        Returns:
            list: List of lines read from the file.
        """
        with open(self.outputfile) as f:
            lines = f.readlines()
            print("read", self.outputfile)
        lines2 = []
        for x in lines:
            lines2.append(x.rstrip())
        del lines
        return lines2

    def read_freq(self) -> dict:
        """
        Reads the frequency of patterns from the LCM output.

        Returns:
            dict: Dictionary containing the frequency and items.
        """
        lines = self.read_lines()
        items = []
        freq = []
        for x in lines:
            s = x.split()
            # print("read_freq, s", s)
            items_tr = self.inverse_transform_items(s[:-1])
            items.append(items_tr)
            fr = s[-1].replace("(", "").replace(")", "")
            freq.append(int(fr))
        self.items = items
        self.freq = freq
        del lines
        return {"frequency": freq, "items": items}

    def read_rule(self) -> dict:
        """
        Reads the rules from the LCM output.

        Returns:
            dict: Dictionary containing frequency, confidence, source items, and target items.
        """
        lines = self.read_lines()
        # rulelist = []
        item_source_list = []
        freq_list = []
        item_target_list = []
        confidence_list = []
        for x in lines:
            s = x.split("<=")
            target = s[0]
            source = s[1]
            st = target.split()
            item_target = st[1]
            confidence = st[0].replace("(", "").replace(")", "").split(",")

            ss = source.split()
            item_source = ss[:-1]
            support = ss[-1].replace("(", "").replace(")", "")

            # rulelist.append( [item_source, support, item_target, confidence, ])
            item_source_list.append(item_source)
            freq_list.append(support)
            item_target_list.append(item_target)
            confidence_list.append(confidence[0])
        # self.rulelist = rulelist
        self.item_source_list = item_source_list
        self.freq_list = freq_list
        self.item_target_list = item_target_list
        self.confidence_list = confidence_list
        return {"frequency": freq_list, "confidence": confidence_list,
                "source_items": self.inverse_transform_transaction(item_source_list),
                "target_item": self.inverse_transform_items(item_target_list)}
#        return self.inverse_transform_rules(rulelist)

    def read(self) -> dict:
        """
        Reads the result from the LCM output based on the mode (frequency or rule).

        Returns:
            dict: Dictionary containing the results, either frequency or rules.
        """
        if self.rule_for_item is not None:
            return self.read_rule()
        else:
            return self.read_freq()


if __name__ == "__main__":
    import pandas as pd

    transactions = [
        ["apple", "banana", "cherry"],
        ["apple", "banana"],
        ["apple", "grape"],
        ["banana", "cherry"],
        ["apple", "banana", "grape"],
        ["cherry"],
        ["banana", "grape"],
        ["apple", "grape"],
        ["apple", "banana", "cherry", "grape"],
        ["apple", "banana", "grape"]
    ]
    lcm = LCM("lcm53/lcm", transactions)

    # freqnency mining
    lcm.run()
    print(pd.DataFrame(lcm.read()))

    # freqnency mining
    lcm.run(target="cherry")
    print(pd.DataFrame(lcm.read()))

    # rule mining
    lcm.run(rule_for_item="banana")
    print(pd.DataFrame(lcm.read()))
