from typing import Union
import subprocess
import os


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
            raise RuntimeError("faild to find the program {}.".format(prog))

        self.transaction = transaction
        self.transactionfile = transactionfile
        self.outputfile = outputfile

        # print("transaction length=", len(transaction))
        _ = self.transform_transaction(self.transaction)

    def transform_transaction(self, transaction: list) -> list:
        """
        Transforms string transactions into numerical transactions.

        Args:
            transaction (list): List of transactions.

        Returns:
            list: List of transformed transactions.
        """
        # make itemlist
        itemlist = []
        for x in transaction:
            itemlist.extend(x)
        itemlist = list(set(itemlist))
        self.itemlist = itemlist
        # 双方向dicの作成
        item_name2id = {}
        item_id2name = {}
        for i, x in enumerate(itemlist):
            item_name2id[x] = i + 1
            item_id2name[str(i + 1)] = x
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

    def transform_items(self, items: Union[list, str]) -> list:
        """
        Transforms a list or string of items into numerical format.

        Args:
            items (list or str): List or string of items to be transformed.

        Returns:
            list or int: Transformed items in numerical format.
        """
        if isinstance(items, list):
            itemsout = []
            for x in items:
                itemsout.append(self.item_name2id[x])
        elif isinstance(items, str):
            itemsout = self.item_name2id[items]
        return itemsout

    def inversetransform_items(self, items: Union[list, str]) -> list:
        """
        Inverse transforms a list or string of items from numerical back to their original format.

        Args:
            items (list or str): List or string of items in numerical format to be inverse transformed.

        Returns:
            list or str: Original format of items.
        """
        if isinstance(items, list):
            itemsout = []
            for x in items:
                itemsout.append(self.item_id2name[x])
        elif isinstance(items, str):
            itemsout = self.item_id2name[items]
        return itemsout

    def inversetransform_itemslist(self, itemslist: list) -> list:
        """
        Inverse transforms a list of items lists from numerical back to their original format.

        Args:
            itemslist (list of list): List of items lists in numerical format to be inverse transformed.

        Returns:
            list of list: Original format of items lists.
        """
        rulelist2 = []
        for rule in itemslist:
            rule2 = self.inversetransform_items(rule)
            rulelist2.append(rule2)
        return rulelist2

    def run(self, min_support: int = 1, itemset_mining: str = "closed_frequent",
            rule_for_item: Union[list, None] = None, target: Union[list, None] = None,
            option: dict = {}) -> int:
        """
        Executes the LCM program with the specified parameters.

        Args:
            min_support (int, optional): Minimum support threshold. Defaults to 1.
            itemset_mining (str, optional): Mining type, one of "frequent", "closed_frequent", "maximal_frequent", "positive-closed". Defaults to "closed_frequent".
            rule_for_item (list or None, optional): Specific item to find rules for. Defaults to None.
            target (list or None, optional): Specific target to mine. Defaults to None.
            option (dict, optional): Additional LCM command options. Defaults to empty dictionary.

        Returns:
            int: Return code from the subprocess call to the LCM program.
        """
        itemset_mining_dic = {"frequent": "F", "closed_frequent": "C", "maximal_frequent": "M",
                              "positive-closed": "P"}
        option_default = {"min_confidence": 0.5, "min_itemset_size": 1}  # ,"output_num_most_frequent_items":100}

        self.min_support = min_support

        self.itemset_mining = itemset_mining

        option_default.update(option)
        option = option_default

        self.rule_for_item = rule_for_item
        self.target = target

        optadd = []

        if rule_for_item is not None and target is not None:
            print("don't add both rule_for_item and target")
            raise RuntimeError("don't add both rule_for_item and target")

        if rule_for_item is not None and target is None:
            opt = "{}fRs".format(itemset_mining_dic[itemset_mining])
            if option:
                if "min_confidence" in option:
                    optadd = ["-a {}".format(option["min_confidence"])]
                if "max_confidence" in option:
                    optadd = ["-A {}".format(option["max_confidence"])]
                if "min_itemset_size" in option:
                    optadd.append("-l {}".format(option["min_itemset_size"]))
                if "max_itemset_size" in option:
                    optadd.append("-u {}".format(option["max_itemset_size"]))

            if len(rule_for_item) > 0:
                targetid = self.transform_items(rule_for_item)
                optadd.append("-i {}".format(targetid))
            with open(self.transactionfile, "w") as f:
                for x in self.transaction_transformed:
                    y = " ".join(list(map(str, x)))
                    f.write(y + "\n")
                print(self.transactionfile, "is made.")

        if rule_for_item is None and target is not None:
            opt = "{}fs".format(itemset_mining_dic[itemset_mining])
            targetid = self.transform_items(target)
            if option:
                if "min_itemset_size" in option:
                    optadd.append("-l {}".format(option["min_itemset_size"]))
                if "max_itemset_size" in option:
                    optadd.append("-u {}".format(option["max_itemset_size"]))

                # if "output_num_most_frequent_items" in option:
                #    optadd.append( "-K {}".format(option["output_num_most_frequent_items"]) )
            with open(self.transactionfile, "w") as f:
                for x in self.transaction_transformed:
                    # print(x)
                    if targetid in x:
                        # print("accept")
                        y = " ".join(list(map(str, x)))
                        f.write(y + "\n")
                print(self.transactionfile, "is made.")

        if target is None and rule_for_item is None:
            opt = "{}Rfs".format(itemset_mining_dic[itemset_mining])
            # targetid = self.transform_items(target)
            # print("targetid",targetid)
            # optadd.append( "-l 1" )
            with open(self.transactionfile, "w") as f:
                for x in self.transaction_transformed:
                    # print(x)
                    if True:
                        # print("accept")
                        y = " ".join(list(map(str, x)))
                        f.write(y + "\n")
                print(self.transactionfile, "is made.")

        cmd = "{} {} {} {} {} {}".format(self.prog, opt, " ".join(optadd),
                                         self.transactionfile, self.min_support, self.outputfile)
        print("command", cmd)
        # subprocess.call(cmd,shell=True)
        proc = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
            items_tr = self.inversetransform_items(s[:-1])
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
                "source_items": self.inversetransform_itemslist(item_source_list),
                "target_item": self.inversetransform_itemslist(item_target_list)}
#        return self.inversetransform_rules(rulelist)

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
