"""
BORIS
Behavioral Observation Research Interactive Software
Copyright 2012-2019 Olivier Friard

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
  MA 02110-1301, USA.
"""

from config import *
import utilities
import time
import tablib



def instantaneous_sampling(pj: dict,
                           selected_observations: list,
                           parameters_obs: dict,
                           time_interval: float) -> dict:
    """
    Instantaneous samplig analysis

    Args:
        pj (dict): project dictionary
        selected_observations (list): list of selected observations
        parameters_obs (dict): dcit of parameters
        time_interval (float): time interval (in seconds)

    Returns:
        dict: dictionary of tablib dataset

    """

    results_df = {}

    state_behavior_codes = [x for x in utilities.state_behavior_codes(pj[ETHOGRAM]) if x in parameters_obs[SELECTED_BEHAVIORS]]

    for obs_id in selected_observations:

        if obs_id not in results_df:
            results_df[obs_id] = {}

        for subject in parameters_obs[SELECTED_SUBJECTS]:

            # extract tuple (behavior, modifier)
            behav_modif_list = [(idx[2], idx[3])
                                for idx in pj[OBSERVATIONS][obs_id][EVENTS] if idx[1] == (subject if subject != NO_FOCAL_SUBJECT else "")]

            # extract observed subjects NOT USED at the moment
            observed_subjects = [event[1] for event in pj[OBSERVATIONS][obs_id][EVENTS]]

            # add selected behavior if not found in (behavior, modifier)
            if not parameters_obs[EXCLUDE_BEHAVIORS]:
                for behav in parameters_obs[SELECTED_BEHAVIORS]:
                    if behav not in [x[0] for x in behav_modif_list]:
                        behav_modif_list.append((behav, ""))

            behav_modif_set = set(behav_modif_list)

            if parameters_obs[INCLUDE_MODIFIERS]:
                results_df[obs_id][subject] = tablib.Dataset(headers=["time"] + [f"{x[0]}" + f" ({x[1]})" * (x[1] != "")
                                                                                 for x in sorted(behav_modif_set)])
            else:
                results_df[obs_id][subject] = tablib.Dataset(headers=["time"] + [x[0] for x in sorted(behav_modif_set)])

            if subject == NO_FOCAL_SUBJECT:
                sel_subject_dict = {"": {SUBJECT_NAME: ""}}
            else:
                sel_subject_dict = dict([(idx, pj[SUBJECTS][idx]) for idx in pj[SUBJECTS] if pj[SUBJECTS][idx][SUBJECT_NAME] == subject])

            row_idx = 0
            t = parameters_obs[START_TIME]
            while t < parameters_obs[END_TIME]:

                current_states = utilities.get_current_states_modifiers_by_subject(state_behavior_codes,
                                                                                   pj[OBSERVATIONS][obs_id][EVENTS],
                                                                                   sel_subject_dict,
                                                                                   t,
                                                                                   include_modifiers=parameters_obs[INCLUDE_MODIFIERS])

                cols = [float(t)]  # time

                for behav in results_df[obs_id][subject].headers[1:]:  # skip time
                    cols.append(int(behav in current_states[list(current_states.keys())[0]]))

                results_df[obs_id][subject].append(cols)

                t += time_interval
                row_idx += 1

    return results_df