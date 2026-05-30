import wx
import wx.stc as stc
from TextEditor import TextEditor
import difflib


class CompareDlg(wx.Frame):
    def __init__(self, parent, lstc, rstc):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"Compare",
                           pos=wx.DefaultPosition, size=(1024, 768),
                           style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.parent = parent
        self.te1 = TextEditor(self, None, None)
        self.te2 = TextEditor(self, None, None)
        
        # Copy settings
        self.te1.set_lang(lstc.lang)
        self.te2.set_lang(rstc.lang)
        
        # Make them read-only for comparison (will enable briefly to set text)
        self.te1.SetReadOnly(False)
        self.te2.SetReadOnly(False)

        self.SetMinSize((800, 600))

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        self.middle_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.Add(self.middle_sizer, 1, wx.EXPAND)

        self.middle_sizer.Add(self.te1, 1, wx.EXPAND)
        
        # Spacer for connecting lines
        self.spacer = wx.Panel(self, size=(30, -1))
        self.spacer.Bind(wx.EVT_PAINT, self.on_paint_spacer)
        self.middle_sizer.Add(self.spacer, 0, wx.EXPAND)
        
        self.middle_sizer.Add(self.te2, 1, wx.EXPAND)

        # Use IDs for syncing scroll
        self.ID_SYNC_SCROLL_L = wx.NewIdRef()
        self.ID_SYNC_SCROLL_R = wx.NewIdRef()

        self.te1.Bind(stc.EVT_STC_UPDATEUI, self.on_scroll_1, id=self.ID_SYNC_SCROLL_L)
        self.te2.Bind(stc.EVT_STC_UPDATEUI, self.on_scroll_2, id=self.ID_SYNC_SCROLL_R)

        # Add a toolbar for navigation
        self.toolbar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.TB_TEXT)
        self.ID_NEXT = wx.NewIdRef()
        self.ID_PREV = wx.NewIdRef()
        
        self.toolbar.AddTool(self.ID_PREV, "Previous", wx.ArtProvider.GetBitmap(wx.ART_GO_UP, wx.ART_TOOLBAR))
        self.toolbar.AddTool(self.ID_NEXT, "Next", wx.ArtProvider.GetBitmap(wx.ART_GO_DOWN, wx.ART_TOOLBAR))
        self.toolbar.Realize()
        
        self.Bind(wx.EVT_TOOL, self.on_prev_change, id=self.ID_PREV)
        self.Bind(wx.EVT_TOOL, self.on_next_change, id=self.ID_NEXT)

        self.changes = [] # Store line numbers of changes
        self.do_compare(lstc.GetText(), rstc.GetText())
        
        self.te1.SetReadOnly(True)
        self.te2.SetReadOnly(True)
        self.Layout()

    def on_scroll_1(self, event):
        if self.te2.GetFirstVisibleLine() != self.te1.GetFirstVisibleLine():
            self.te2.SetFirstVisibleLine(self.te1.GetFirstVisibleLine())
        if self.te2.GetXOffset() != self.te1.GetXOffset():
            self.te2.SetXOffset(self.te1.GetXOffset())
        if self.te2.GetZoom() != self.te1.GetZoom():
            self.te2.SetZoom(self.te1.GetZoom())
        self.spacer.Refresh()
        event.Skip()

    def on_scroll_2(self, event):
        if self.te1.GetFirstVisibleLine() != self.te2.GetFirstVisibleLine():
            self.te1.SetFirstVisibleLine(self.te2.GetFirstVisibleLine())
        if self.te1.GetXOffset() != self.te2.GetXOffset():
            self.te1.SetXOffset(self.te2.GetXOffset())
        if self.te1.GetZoom() != self.te2.GetZoom():
            self.te1.SetZoom(self.te2.GetZoom())
        self.spacer.Refresh()
        event.Skip()

    def on_paint_spacer(self, event):
        dc = wx.AutoBufferedPaintDC(self.spacer)
        dc.Clear()
        
        gc = wx.GraphicsContext.Create(dc)
        if not gc:
            return

        w, h = self.spacer.GetSize()
        
        # We need to get the actual vertical pixel positions from STC
        # TextHeight(0) might not be accurate if there's zooming or different styles
        
        first_line = self.te1.GetFirstVisibleLine()
        last_line = first_line + self.te1.LinesOnScreen()
        
        # Colors for blocks
        col_del = self.col_del
        col_ins = self.col_ins
        col_rep = self.col_rep
        
        # To handle multi-line blocks nicely, we can group them
        i = first_line
        while i <= min(last_line, self.te1.GetLineCount() - 1):
            ltype = self.line_types[i]
            if ltype == 'equal':
                i += 1
                continue
            
            start_i = i
            while i < min(last_line, self.te1.GetLineCount() - 1) and self.line_types[i+1] == ltype:
                i += 1
            
            # Now we have a block from start_i to i
            y1 = self.te1.GetLineDisplayIndex(start_i) # This might not be what we want
            # PointFromPosition gives client coordinates
            pos1 = self.te1.PositionFromLine(start_i)
            pt1 = self.te1.PointFromPosition(pos1)
            
            pos2 = self.te1.PositionFromLine(i)
            pt2 = self.te1.PointFromPosition(pos2)
            line_h = self.te1.TextHeight(i)
            
            block_y_start = pt1.y
            block_y_end = pt2.y + line_h
            
            if ltype == 'delete':
                gc.SetBrush(wx.Brush(col_del))
            elif ltype == 'insert':
                gc.SetBrush(wx.Brush(col_ins))
            elif ltype == 'replace':
                gc.SetBrush(wx.Brush(col_rep))
            
            # Draw a trapezoid-like shape or just a rectangle for now since they are aligned
            path = gc.CreatePath()
            path.MoveToPoint(0, block_y_start)
            path.AddLineToPoint(w, block_y_start)
            path.AddLineToPoint(w, block_y_end)
            path.AddLineToPoint(0, block_y_end)
            path.CloseSubpath()
            gc.FillPath(path)
            
            i += 1

    def on_prev_change(self, event):
        if not self.changes:
            return
        curr_line = self.te1.GetFirstVisibleLine()
        target_line = self.changes[0]
        for line in reversed(self.changes):
            if line < curr_line:
                target_line = line
                break
        self.te1.ScrollToLine(target_line)
        self.te2.ScrollToLine(target_line)

    def on_next_change(self, event):
        if not self.changes:
            return
        curr_line = self.te1.GetFirstVisibleLine()
        target_line = self.changes[-1]
        for line in self.changes:
            if line > curr_line:
                target_line = line
                break
        self.te1.ScrollToLine(target_line)
        self.te2.ScrollToLine(target_line)

    def do_compare(self, text1, text2):
        lines1 = text1.splitlines(keepends=True)
        lines2 = text2.splitlines(keepends=True)

        # SequenceMatcher works better when strings are stripped of newlines for line comparison
        # but we need to keep track of newlines for display.
        # Actually, splitlines(keepends=True) is fine, but it might treat "line\n" and "line"
        # as different which is what we want if we want to show trailing newline differences.
        
        # Use SequenceMatcher for more robust diffing that identifies replacements
        sm = difflib.SequenceMatcher(None, lines1, lines2, autojunk=False)
        
        aligned1 = []
        aligned2 = []
        # types: 'equal', 'delete', 'insert', 'replace'
        line_types = [] 

        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                for i in range(i1, i2):
                    aligned1.append(lines1[i])
                    aligned2.append(lines2[j1 + (i - i1)])
                    line_types.append('equal')
            elif tag == 'delete':
                for i in range(i1, i2):
                    aligned1.append(lines1[i])
                    aligned2.append('')
                    line_types.append('delete')
            elif tag == 'insert':
                for j in range(j1, j2):
                    aligned1.append('')
                    aligned2.append(lines2[j])
                    line_types.append('insert')
            elif tag == 'replace':
                # For replacements, we align them side by side as much as possible
                # If the number of lines is different, we fill with empty lines
                count1 = i2 - i1
                count2 = j2 - j1
                max_count = max(count1, count2)
                for k in range(max_count):
                    l1 = lines1[i1 + k] if k < count1 else ''
                    l2 = lines2[j1 + k] if k < count2 else ''
                    aligned1.append(l1)
                    aligned2.append(l2)
                    # If both sides have content, it's a real 'replace' (char-level diff)
                    # If one side is empty, it's effectively an insert or delete within a replace block
                    if k < count1 and k < count2:
                        line_types.append('replace')
                    elif k < count1:
                        line_types.append('delete')
                    else:
                        line_types.append('insert')

        self.te1.SetText(''.join(aligned1))
        self.te2.SetText(''.join(aligned2))

        # Indicators for line-level highlighting
        # 20: deletion (left), 21: addition (right), 22: change (both)
        # Indicators for character-level highlighting (darker)
        # 23: char-deletion (left), 24: char-addition (right)

        def setup_indicator(te, id, color, alpha=100):
            te.IndicatorSetStyle(id, stc.STC_INDIC_ROUNDBOX)
            te.IndicatorSetForeground(id, color)
            te.IndicatorSetAlpha(id, alpha)
            te.IndicatorSetOutlineAlpha(id, alpha)
            te.IndicatorSetUnder(id, True)

        # Better colors matching common diff tools
        # Deletions: Light Red background
        # Additions: Light Green background
        # Replacements: Light Blue background
        
        self.col_del = wx.Colour(255, 200, 200) 
        self.col_ins = wx.Colour(200, 255, 200)
        self.col_rep = wx.Colour(220, 230, 255)
        
        self.col_del_strong = wx.Colour(255, 150, 150)
        self.col_ins_strong = wx.Colour(150, 255, 150)

        setup_indicator(self.te1, 20, self.col_del, 180)
        setup_indicator(self.te2, 21, self.col_ins, 180)
        setup_indicator(self.te1, 22, self.col_rep, 180)
        setup_indicator(self.te2, 22, self.col_rep, 180)
        
        setup_indicator(self.te1, 23, self.col_del_strong, 220)
        setup_indicator(self.te2, 24, self.col_ins_strong, 220)

        self.changes = []
        self.line_types = line_types
        for i, ltype in enumerate(line_types):
            # STC positions use 0-based indices for characters
            # PositionFromLine(i) returns the start position of line i
            # GetLineLength(i) returns the length of line i including newline characters
            start1 = self.te1.PositionFromLine(i)
            length1 = self.te1.GetLineLength(i)
            start2 = self.te2.PositionFromLine(i)
            length2 = self.te2.GetLineLength(i)

            if ltype != 'equal':
                if not self.changes or self.changes[-1] != i:
                    self.changes.append(i)

            if ltype == 'delete':
                self.te1.MarkerAdd(i, self.te1.MARKER_MINUS)
                if length1 > 0:
                    self.te1.SetIndicatorCurrent(20)
                    self.te1.IndicatorFillRange(start1, length1)
            elif ltype == 'insert':
                self.te2.MarkerAdd(i, self.te2.MARKER_PLUS)
                if length2 > 0:
                    self.te2.SetIndicatorCurrent(21)
                    self.te2.IndicatorFillRange(start2, length2)
            elif ltype == 'replace':
                # Line level highlight
                if length1 > 0:
                    self.te1.SetIndicatorCurrent(22)
                    self.te1.IndicatorFillRange(start1, length1)
                if length2 > 0:
                    self.te2.SetIndicatorCurrent(22)
                    self.te2.IndicatorFillRange(start2, length2)
                
                # Character level diff
                s1 = aligned1[i]
                s2 = aligned2[i]
                char_sm = difflib.SequenceMatcher(None, s1, s2)
                for ctag, ci1, ci2, cj1, cj2 in char_sm.get_opcodes():
                    if ctag == 'delete':
                        self.te1.SetIndicatorCurrent(23)
                        self.te1.IndicatorFillRange(start1 + ci1, ci2 - ci1)
                    elif ctag == 'insert':
                        self.te2.SetIndicatorCurrent(24)
                        self.te2.IndicatorFillRange(start2 + cj1, cj2 - cj1)
                    elif ctag == 'replace':
                        self.te1.SetIndicatorCurrent(23)
                        self.te1.IndicatorFillRange(start1 + ci1, ci2 - ci1)
                        self.te2.SetIndicatorCurrent(24)
                        self.te2.IndicatorFillRange(start2 + cj1, cj2 - cj1)
