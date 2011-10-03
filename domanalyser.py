#!/usr/bin/python3
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#       
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#       
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# Developed by: Nasel(http://www.nasel.com.ar)
# 
# Authors:
# Santiago Alessandri
# Matías Fontanini
# Gastón Traberg


import lxml.html as lxml
import chardet
from functools import reduce

class DomAnalyser():
    def __init__(self):
        self.encoding = None
    
    def decode(self, data):
        if self.encoding is None:
            self.encoding = chardet.detect(data)['encoding']
        try:
            return data.decode(self.encoding)
        except UnicodeDecodeError:
            self.encoding = chardet.detect(data)['encoding']
            return data.decode(self.encoding)
    
    def set_good_page(self, page, search_needle):
        dom_page = lxml.fromstring(self.decode(page))
        self._good_index_list = DomAnalyser._dfs(dom_page, [search_needle])
        if not self._good_index_list:
            raise NeedleNotFound()
        self._good_content = DomAnalyser._lookup_node(dom_page,
                                                      self._good_index_list)
        del dom_page
    
    def is_valid(self, page):
        dom_page = lxml.fromstring(self.decode(page))
        content_on_page = DomAnalyser._lookup_node(dom_page,
                                                   self._good_index_list)
        del dom_page
        return content_on_page == self._good_content
    
    def find_needles(self, page, needles):
        dom_page = lxml.fromstring(self.decode(page))
        index_list = DomAnalyser._dfs(dom_page, [needles])
        if not index_list:
            return None
        content = DomAnalyser._lookup_node(dom_page, index_list)
        return next(n for n in needles if needles in content)
    
    def node_content(self, page):
        return DomAnalyser._lookup_node(lxml.fromstring(self.decode(page)), self._good_index_list)

    @classmethod
    def _dfs(cls, dom, search_needles, index_list=[]):
        node_value = DomAnalyser._join_text(dom)
        if node_value is None:
            node_value = ""
        for needle in search_needles:
            if needle in node_value:
                return index_list
        for i in range(len(dom)):
            index_list.append(i)
            tmp_res = cls._dfs(dom[i], search_needles, index_list)
            if tmp_res:
                return index_list
            index_list.pop()
        return None
    
    @classmethod
    def _join_text(cls, node):
        return (node.text and node.text or '') + ''.join(map(lambda x: x.tail and x.tail or '', node))
    
    @classmethod
    def _lookup_node(cls, dom, index_list):
        try:
            node = reduce(
                    lambda node, index: node[index],
                    index_list, dom)
            return DomAnalyser._join_text(node)
        except IndexError:
            return None

class NeedleNotFound(Exception):
    pass
