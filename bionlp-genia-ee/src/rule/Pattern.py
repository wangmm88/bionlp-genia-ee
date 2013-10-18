'''
Created on Oct 2, 2013

@author: Andresta
'''

class Pattern(object):
    '''
    classdocs
    '''
    def __init__(self):
        pass
    
    def get_pattern_str(self, position):
        """
        return string template of a given node position
        """
        string = ''
        for _, node in sorted(position.iteritems()):
            string += node + '-'
        return string.rstrip('-')
    
    def is_chunk(self, o_sen, t_wn, arg1, arg2 = -1):
        """
        return true if event relation is in chunk layer 
        """
        o_chunk = o_sen.chunk
        
        retval = o_chunk.same_chunk(t_wn, arg1)
        if arg2 >= 0:
            retval = retval and o_chunk.same_chunk(t_wn, arg2)
            
        return retval
    
    def is_phrase(self, o_sen, t_wn, arg1, arg2 = -1):
        """
        return true if event relation is in phrase layer 
        """
        o_chk = o_sen.chunk
        retval = False
         
        t_chk = o_chk.chunk_map[t_wn]
        a1_chk = o_chk.chunk_map[arg1]
        if arg1 > t_wn:
            if 'PP' in o_chk.chunk_type[t_chk:a1_chk]: retval = True
        
        if arg2 > t_wn:
            a2_chk = o_chk.chunk_map[arg2]
            if 'PP' in o_chk.chunk_type[t_chk:a2_chk]: retval = True
            
        return retval
      
    def get_distance_chkdep(self, o_sen, node1, node2):
        """
        return distance from node1 to node2 using chunk and dependency
        """  
        o_dep = o_sen.dep
        o_chunk = o_sen.chunk
        chunks = []
        
        upath = o_dep.get_shortest_path(node1, node2, 'undirected')
        for node in upath:
            chunks.append(o_chunk.chunk_map[node])
            
        return len(set(chunks)) - 1
    
    def get_prep_word(self, o_sen, trig_wn, arg_wn):
        """
        return tuple of prepositions (string,word_number)                
        """
        o_chunk = o_sen.chunk
        preps_word = []
        trig_chk_num = o_chunk.chunk_map[trig_wn]
        arg_chk_num = o_chunk.chunk_map[arg_wn]
        for chk_num in range(trig_chk_num+1, arg_chk_num):
            prep = o_chunk.prep_chunk.get(chk_num,None)
            if prep != None:
                preps_word.append(prep)                
        
        return preps_word
    
    def get_pattern_1arg(self, o_sen, t_wn, arg1):
        """
        return pattern, layer, and preposition 1 string
        """
        prep_string = ''
        layer = ''
        tword = o_sen.words[t_wn]
        position = {t_wn:'trig', arg1:'arg1'}
        
        if self.is_chunk(o_sen, t_wn, arg1):            
            layer = 'chunk'    
            
        elif self.is_phrase(o_sen, t_wn, arg1):                        
            layer = 'phrase'            
            # get preposition, if more than 1 get the nearest prep to argument
            preps = self.get_prep_word(o_sen,t_wn, arg1)
            prep_string = preps[-1][0] 
            prep_wn = preps[-1][1]
            position[prep_wn] = 'prep1'
        # no clause layer with only 1 argument
        #elif tword['pos_tag'][0:2] == 'VB':
        #    layer = 'clause'
        
        # build template type
        pattern_string = self.get_pattern_str(position) if layer != '' else ''
        
        return pattern_string, layer, prep_string

    def get_pattern_2arg(self, o_sen, t_wn, arg1, arg2):
        """
        return pattern, layer, and preposition 1 string
        """
        prep1_string = ''
        prep2_string = ''
        layer = ''
        tword = o_sen.words[t_wn]
        position = {t_wn:'trig', arg1:'arg1', arg2:'arg2'}
        
        if self.is_chunk(o_sen, t_wn, arg1, arg2):            
            layer = 'chunk'                
        elif self.is_phrase(o_sen, t_wn, arg1, arg2):            
            layer = 'phrase'            
            # get preposition, if more than 1 get the nearest prep to argument
            preps1 = []
            preps2 = []
            if arg1 > t_wn:
                preps1 = self.get_prep_word(o_sen,t_wn, arg1)
            if arg2 > t_wn:
                preps2 = self.get_prep_word(o_sen, t_wn, arg2)
            if preps1 != []:            
                prep1_string = preps1[-1][0] 
                prep1_wn = preps1[-1][1]
                position[prep1_wn] = 'prep1'
            if preps2 != [] and preps2 != preps1:    
                prep2_string = preps2[-1][0] 
                prep2_wn = preps2[-1][1]
                position[prep2_wn] = 'prep2'
            if prep1_string == '' and prep2_string == '':
                #print o_sen.number, t_wn, arg1, arg2
                raise ValueError('NO preprosition found')
        elif tword['pos_tag'][0:2] == 'VB':
            layer = 'clause'
            
        # build template type
        pattern_string = self.get_pattern_str(position) if layer != '' else ''
        
        return pattern_string, layer, prep1_string, prep2_string

class TemplatePattern(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''    
        self.pos = ''
        self.template = []
            
        # preposition
        self.prep1 = []
        self.prep2 = []
        
        # distance
        self.dist1 = []
        self.dist2 = []
        
        # protein counter
        self.pro1_count = 0
        self.evt1_count = 0
        
        # protein 2 counter
        self.pro2_count = 0
        self.evt2_count = 0
        
        self.freq = 0
        
    def set(self, dist1, arg1_type, prep1='', dist2=-1, arg2_type='', prep2=''):
        
        """ set argument 1 """
        if dist1 not in self.dist1:
            self.dist1.append(dist1)
            
        if arg1_type == 'Protein':
            self.pro1_count+=1
        else:
            self.evt1_count+=1
        
        if prep1 != '' and prep1 not in self.prep1:
            self.prep1.append(prep1)
        
        """ optionally, set argument 2 """
        if dist2 != -1 and dist2 not in self.dist2:
            self.dist2.append(dist2)
            
        if arg2_type == 'Protein':
            self.pro2_count+=1
        else:
            self.evt2_count+=1
            
        if prep2 != '' and  prep2 not in self.prep2:
            self.prep2.append(prep2)
            
        # increase frequency
        self.freq += 1

    def prints(self):
        print 'frequency:', self.freq
        print 'argument 1'
        print 'prep1:', self.prep1
        print 'dist1:', sorted(self.dist1)
        print '# arg1 pro:', self.pro1_count
        print '# arg1 evt:', self.evt1_count
        print 'argument 2'
        print 'prep2:', self.prep2
        print 'dist2:', sorted(self.dist2)
        print '# arg2 pro:', self.pro2_count
        print '# arg2 evt:', self.evt2_count
        


class ExtractionPattern(object):
    
    def __init__(self, tc, t_string, pos_tag, arg1, arg2 = -1):
        
        self.tc = tc
        self.arg1 = arg1
        self.arg2 = arg2
        
        self.t_string = t_string.lower()
        self.pos = pos_tag
        
        self.container = ''
        self.pattern_type = ''
        
        self.freq = 0
        
        # preposition
        self.prep1 = ''
        self.prep2 = ''
        
        # distance
        self.dist1 = -1
        self.dist2 = -1
        
        # argument type
        self.arg1_type = 'null'
        self.arg2_type = 'null'
        
    def has_arg2(self):
        return self.dist2 != -1
    
    def get_key(self):
        return ':'.join([self.t_string,self.pos, self.pattern_type, self.container])
    
    def prints(self):
        print '================================================'
        print 'key:', self.get_key()
        print self.container, '=>', self.pattern_type     
        print 'freq:', self.freq   
        print 'trigger:', self.tc, self.t_string, self.pos
        print '-------'
        print self.arg1 ,'-', self.arg1_type
        print 'dist1:', self.dist1
        print 'prep1:',self.prep1
        if self.arg2!= -1:
            print '-------'
            print self.arg2 ,'-', self.arg2_type
            print 'dist2:', self.dist2
            print 'prep2:',self.prep2
        
    