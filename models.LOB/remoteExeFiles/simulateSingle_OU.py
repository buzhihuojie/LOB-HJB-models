'''
Created on Mar 5, 2015

@author: weiluo
'''
from remoteExeFiles.SaveObj_helpers import basicReader
from remoteExeFiles.SimulateSingle import constructFileName, prepareOptionsHelper,\
summary_mean_var_helper,prepareOptionsHelper2, dumpData, summary_mean_var_constantPrice_helper
from remoteExeFiles.SimulateComparison import simulateImplicitComparison
from abstractLOB.poisson_OU_explicit import Poisson_explicit_OU_LOB
from abstractLOB.poisson_OU_implicit import Poisson_OU_implicit, Poisson_OU_implicit_truncateControlAtZero

def prepareOptions():
    myReader = basicReader()
    parser = prepareOptionsHelper(myReader)
    
    parser.add_argument('-alpha', type = float, nargs='?',\
                        help="mean-reverting rate")
    
    parser.add_argument('-half_S', type=float, nargs="?",\
                        help="radius of space we consider around s_0")
    
    parser.add_argument('-half_I_S', type=int, nargs='?',\
                        help="number of grid points of half of s space")
    parser.add_argument('-s_long_term_mean', type=float, nargs='?',\
                        help='long term mean of the OU price process')
    
    options = myReader.parserToArgsDict(parser)
    options.pop("type")
    options.pop("BC")
    return prepareOptionsHelper2(options)

def prepareOptions_forSameRandomness():
    
    myReader = basicReader()
    parser = prepareParserHelper(myReader)
    options = myReader.parserToArgsDict(parser)
    options.pop("type")
    options.pop("BC")
    return prepareOptionsHelper3(options)
def prepareParserHelper(myReader):
    
    parser = prepareOptionsHelper(myReader)
    
    parser.add_argument('-alpha', type = float, nargs='?',\
                        help="mean-reverting rate")
    parser.add_argument('-lambda_tilde', type = float, nargs='?',\
                        help="left inventory penalty")
    parser.add_argument('-half_S', type=float, nargs="?",\
                        help="radius of space we consider around s_0")
    
    parser.add_argument('-half_I_S', type=int, nargs='?',\
                        help="number of grid points of half of s space")
    parser.add_argument('-s_long_term_mean', type=float, nargs='?',\
                        help='long term mean of the OU price process')
    parser.add_argument('-new_weight', type=float, nargs='?',\
                        help='weight of new iteration result in the iteration')
    parser.add_argument('-abs_threshold_power', type=float, nargs='?',\
                        help="the power of absolute threshold for determining when to stop the iteration")
    parser.add_argument('-rlt_threshold_power', type=float, nargs='?',\
                        help="the power of relative threshold for determining when to stop the iteration")
    parser.add_argument('-iter_max', type=float, nargs='?',\
                        help="max number of iteration")
    
    _truncation_option = 0 #0: both, 1: truncation only, 2: no truncation only.
    parser.add_argument('-truncation_option', type = int, default = _truncation_option,\
                        nargs = '?', help="number of trajectories to simulate")
    return parser
def prepareOptions_forSaveSampleValueFunction():
    myReader = basicReader()
    parser = prepareParserHelper(myReader)
    _sample_stepSize = 100
    parser.add_argument('-sample_stepSize', type=int, nargs='?',default = _sample_stepSize,\
                        help="the step size for sampling the value function")
    options = myReader.parserToArgsDict(parser)
    options.pop("type")
    options.pop("BC")
    options_forImplicit, options_forExplicit,  simulate_num, fileName, random_q_0, truncation_option \
    = prepareOptionsHelper3(options)
    sample_stepSize = options["sample_stepSize"]
    options_forImplicit.pop("sample_stepSize")
    return [options_forImplicit, simulate_num, fileName, sample_stepSize]
    
def prepareOptionsHelper3(options):
    directory = options['dump_dir']
    options.pop('dump_dir')

    fileName = constructFileName(options, directory)
    simulate_num = options['simulate_num']
    options.pop('simulate_num')
    
    random_q_0  =  options['random_q_0'].upper()
    truncation_option = options['truncation_option']
    if 'truncation_option' in options:
        options.pop('truncation_option')
    options.pop("random_q_0")
    options_forImplicit = options.copy()
    if "new_weight" in options:
        options.pop('new_weight')
    if "abs_threshold_power" in options:
        options.pop('abs_threshold_power')
    if 'rlt_threshold_power' in options:
        options.pop('rlt_threshold_power')
    if 'iter_max' in options:
        options.pop('iter_max')
    
    options_forExplicit = options.copy()
    return [options_forImplicit, options_forExplicit,  simulate_num, fileName, random_q_0, truncation_option]

def summary_mean_var(options,simulate_num,fileName, randomOpt = False):
    myObj = Poisson_explicit_OU_LOB(**options)
    myObj.run()    
    print "done with run"
    return summary_mean_var_helper(myObj, simulate_num, options, fileName, randomOpt, False)

def simulateImplicitComparison_OU():
    options,  simulate_num, fileName, random_q_0 = prepareOptions()
    fileName += '_comparison'
    random_q_0_opt = False if random_q_0.upper()=="FALSE" else True
    if 'beta' in options and options['beta']==0.0:
        dumpData(summary_mean_var(options,  simulate_num, fileName, random_q_0_opt))
        return
    data = [fileName]
    nonZeroBetaOptions = options.copy()
    zeroBetaOptions = options.copy()
    data.append(summary_mean_var(nonZeroBetaOptions,  simulate_num, fileName, random_q_0_opt))
    zeroBetaOptions['beta'] = 0.0
    data.append(summary_mean_var(zeroBetaOptions,  simulate_num, fileName, random_q_0_opt))
    
    dumpData(data)
    
def simulateImplicitComparison_OU_obj():
    options,  simulate_num, fileName, random_q_0 = prepareOptions()
    fileName += '_comparison'
    random_q_0_opt = False if random_q_0.upper()=="FALSE" else True
    if 'beta' in options and options['beta']==0.0:
        myObj = Poisson_OU_implicit(**options)
        myObj.run()  
        myObj.simulate_forward()
        dumpData([fileName, myObj])
        return
    data = [fileName]
    nonZeroBetaOptions = options.copy()
    zeroBetaOptions = options.copy()
    myObj = Poisson_OU_implicit(**nonZeroBetaOptions)
    myObj.run()  
    myObj.simulate_forward()
    
    data.append(myObj)
    zeroBetaOptions['beta'] = 0.0
    myObj = Poisson_OU_implicit(**zeroBetaOptions)
    myObj.run()  
    myObj.simulate_forward()
    data.append(myObj)
    
    dumpData(data)
    
def simulateComparison_OU_sameRandomness():
    options_forImplicit, options_forExplicit,  simulate_num, fileName, random_q_0 = prepareOptions_forSameRandomness()
    fileName += '_comparison'
    random_q_0_opt = False if random_q_0.upper()=="FALSE" else True
   
    data = [fileName[:200], options_forImplicit]
    
    myObjImplicit = Poisson_OU_implicit_truncateControlAtZero(**options_forImplicit)
    myObjExplicit = Poisson_explicit_OU_LOB(**options_forExplicit)

    myObjImplicit.run()
    myObjExplicit.run()
    sim_data = []
    for _ in xrange(simulate_num):
        randomSource = myObjExplicit.generate_random_source()
        myObjExplicit.simulate_forward(useGivenRandom=True, randomSource=randomSource)
        myObjImplicit.simulate_forward(useGivenRandom=True, randomSource=randomSource)
        tmpdata_explicit = [myObjExplicit.s, myObjExplicit.q, myObjExplicit.x, myObjExplicit.simulate_control_a, myObjExplicit.simulate_control_b,\
                            myObjExplicit.simulate_price_a, myObjExplicit.simulate_price_b]
        tmpdata_implicit = [myObjImplicit.s, myObjImplicit.q, myObjImplicit.x, myObjImplicit.simulate_control_a, myObjImplicit.simulate_control_b, \
                            myObjImplicit.simulate_price_a, myObjImplicit.simulate_price_b]
        sim_data.append([tmpdata_explicit, tmpdata_implicit])
    data.append(sim_data)
    
    dumpData(data)
    
def save_OU_obj_helper():
    options_forImplicit, options_forExplicit,  simulate_num, fileName, random_q_0, truncation_option \
    = prepareOptions_forSameRandomness()
    fileName += '_obj'
    data = [fileName[:200], options_forImplicit]
    if truncation_option == 0 or truncation_option == 1:
        myObjImplicit_truncation = Poisson_OU_implicit_truncateControlAtZero(**options_forImplicit)
        myObjImplicit_truncation.run()
        data.append(myObjImplicit_truncation)
    if truncation_option == 0 or truncation_option == 2:

        myObjImplicit_no_truncation = Poisson_OU_implicit(**options_forImplicit)
        myObjImplicit_no_truncation.run()
        data.append(myObjImplicit_no_truncation)
    return data, simulate_num, truncation_option

def save_OU_constantPrice_helper():
    options_forImplicit, options_forExplicit,  simulate_num, fileName, random_q_0, truncation_option \
    = prepareOptions_forSameRandomness()
    fileName += '_obj'
    data = [fileName[:200], options_forImplicit]
    myObjImplicit_no_truncation = Poisson_OU_implicit(**options_forImplicit)
    myObjImplicit_no_truncation.run()
    data.append(myObjImplicit_no_truncation)
    return data, simulate_num, truncation_option  

def save_OU_sampleValueFunction_helper():
    options_forImplicit, simulate_num, fileName, sample_stepSize\
    = prepareOptions_forSaveSampleValueFunction()
    fileName += '_obj'
    data = [fileName[:200], options_forImplicit]
    myObjImplicit_no_truncation = Poisson_OU_implicit(**options_forImplicit)
    myObjImplicit_no_truncation.run()
    myObjImplicit_no_truncation_unrun = Poisson_OU_implicit(**options_forImplicit)

    data.append(myObjImplicit_no_truncation)
    data.append(myObjImplicit_no_truncation_unrun)
    return data, sample_stepSize


def save_OU_obj():
    data, simulate_num= save_OU_obj_helper()
    dumpData(data)
    
def simulate_OU_checkStd():
    data, simulate_num, truncation_option  = save_OU_obj_helper()
    dump_data = [data[0], data[1]]
    if truncation_option == 0:
        myObjImplicit_truncation = data[2]
        myObjImplicit_no_truncation = data[3]

        dump_data.append(summary_mean_var_helper(myObjImplicit_truncation, simulate_num, data[1], data[0], False, False))
        dump_data.append(summary_mean_var_helper(myObjImplicit_no_truncation, simulate_num, data[1], data[0], False, False))

    if truncation_option == 1:
        myObjImplicit_truncation = data[2]
        dump_data.append(summary_mean_var_helper(myObjImplicit_truncation, simulate_num, data[1], data[0], False, False))
    if truncation_option == 2:
        myObjImplicit_no_truncation = data[2]
        dump_data.append(summary_mean_var_helper(myObjImplicit_no_truncation, simulate_num, data[1], data[0], False, False))
    
    dumpData(dump_data)
    
def simulate_OU_constantPrice():
    data, simulate_num, truncation_option  = save_OU_constantPrice_helper()
    dump_data = [data[0], data[1]]
    myObjImplicit_no_truncation = data[2]
    dump_data.append(summary_mean_var_constantPrice_helper(myObjImplicit_no_truncation, simulate_num, data[1], data[0], False, False))
    dumpData(dump_data)

def save_sampleValueFunction():
    data, sample_stepSize  = save_OU_sampleValueFunction_helper()
    dump_data = [data[0], data[1]]
    myObjImplicit_no_truncation = data[2]
    myObjImplicit_no_truncation_unrun = data[3]
    sample_result = myObjImplicit_no_truncation._result[::sample_stepSize]
    sample_a_price = myObjImplicit_no_truncation._a_price[::sample_stepSize]
    sample_b_price = myObjImplicit_no_truncation._b_price[::sample_stepSize]
    dump_data.append([sample_stepSize, myObjImplicit_no_truncation_unrun, sample_result, sample_a_price, sample_b_price])
    dumpData(dump_data)









