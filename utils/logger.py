import logging
import os
import colorlog
import re
import datetime
from logging import getLogger
from colorama import init


class Logger:

    def __init__(self, config):
        """
        A logger that can show a message on standard output and write it into the
        file named `filename` simultaneously.
        All the message that you want to log MUST be str.

        Args:
            config (Config): An instance object of Config, used to record parameter information.

        Example:
            >>> logger = logging.getLogger(config)
            >>> logger.debug(train_state)
            >>> logger.info(train_result)
        """
        init(autoreset=True)
        LOGROOT = f'./openhgnn/output/{config.model_name}/'
        dir_name = os.path.dirname(LOGROOT)
        ensure_dir(dir_name)

        logfilename = '{}-{}.log'.format(config.model_name, get_local_time())

        logfilepath = os.path.join(LOGROOT, logfilename)

        filefmt = "%(asctime)-15s %(levelname)s  %(message)s"
        filedatefmt = "%a %d %b %Y %H:%M:%S"
        fileformatter = logging.Formatter(filefmt, filedatefmt)

        sfmt = "%(log_color)s%(asctime)-15s %(levelname)s  %(message)s"
        sdatefmt = "%d %b %H:%M"
        sformatter = colorlog.ColoredFormatter(sfmt, sdatefmt, log_colors=log_colors_config)
        if not hasattr(config, 'state') or config.state.lower() == 'info':
            level = logging.INFO
        elif config.state.lower() == 'debug':
            level = logging.DEBUG
        elif config.state.lower() == 'error':
            level = logging.ERROR
        elif config.state.lower() == 'warning':
            level = logging.WARNING
        elif config.state.lower() == 'critical':
            level = logging.CRITICAL
        else:
            level = logging.INFO

        fh = logging.FileHandler(logfilepath, mode='a')
        fh.setLevel(level)
        fh.setFormatter(fileformatter)
        remove_color_filter = RemoveColorFilter()
        fh.addFilter(remove_color_filter)

        sh = logging.StreamHandler()
        sh.setLevel(level)
        sh.setFormatter(sformatter)
        
        root_logger = logging.getLogger()
        for h in root_logger.handlers:
            root_logger.removeHandler(h)

        logging.basicConfig(level=level, handlers=[sh, fh])
        self.logger = getLogger()
        self.logger.info(config)

    def info(self, s):
        self.logger.info(s)
        
    def load_best_config(self, s):
        self.logger.info('[Load Best Config] ' + s)
        
    def train_info(self, s):
        self.logger.info('[Train Info] ' + s)
    
    def metric2str(self, metric_dict):
        out = "[Evaluation metric]"
        for mode, score_dict in metric_dict.items():
            out += f"\tMode:{mode}, "
            for metric, score in score_dict.items():
                out += f"{metric}: {score:.4f}; "
        return out
    
    def dataset_info(self, s):
        self.logger.info('[Dataset Process] ' + s)
        
    def feature_info(self, s):
        self.logger.info('[Feature Transformation] ' + s)
    
    # graph data analyze
    def log_data_info(self, g):
        num_nodes = g.num_nodes()
        num_edges = g.num_edges()
        node_types = len(g.ntypes)
        edge_types = len(g.etypes)
        c_etypes = len(g.canonical_etypes)
        datainfo = {'total nodes':num_nodes, 'total edges':num_edges, 'node types':node_types, 'edge types': edge_types,
                    'c_etypes': c_etypes}

        self.logger.info(datainfo)
        return

    # evaluate results
    def log_eval_info(self, metric, epoch, train_score, train_loss, val_score, val_loss):
        if metric == 'f1_lr':
            eval_info = {f"Epoch: {epoch:03d}, Train_loss: {train_loss:.4f}, Train_macro_f1: {train_score[0]:.4f}, Train_micro_f1: {train_score[1]:.4f}, "
                f"Val_macro_f1: {val_score[0]:.4f}, Val_micro_f1: {val_score[1]:.4f}, ValLoss:{val_loss: .4f}"}

        # use acc
        elif metric == 'acc':
            eval_info = {f"Epoch: {epoch:03d}, Train_loss: {train_loss:.4f}, Train_acc: {train_score:.4f},  "
                f"Val_acc: {val_score:.4f}, ValLoss:{val_loss: .4f}"}

        elif metric == 'acc-ogbn-mag':
            eval_info = {f"Epoch: {epoch:03d}, Train_loss: {train_loss:.4f}, Train_acc: {train_score:.4f},  "
                f"Val_acc: {val_score:.4f}, ValLoss:{val_loss: .4f}"}

        else:
            eval_info = {f"Epoch: {epoch:03d}, Train_loss: {train_loss:.4f}, Train_macro_f1: {train_score[0]:.4f}, Train_micro_f1: {train_score[1]:.4f}, "
                f"Val_macro_f1: {val_score[0]:.4f}, Val_micro_f1: {val_score[1]:.4f}, ValLoss:{val_loss: .4f}"}
        self.logger.info(eval_info)
        return

    def log_metric_info_1(self, metric, score, mode):
        met_info = {f"{mode}_{metric} = {score:.4f}"}
        self.logger.info(met_info)
        return

    def log_metric_info_2(self, metric, score, mode):
        met_info = {f"{mode}_macro_{metric} = {score[0]:.4f}, {mode}_micro_{metric}: {score[1]:.4f}"}
        self.logger.info(met_info)