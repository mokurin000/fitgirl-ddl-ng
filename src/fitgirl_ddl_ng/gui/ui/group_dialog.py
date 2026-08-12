"""Group selection dialog for the fitgirl DDL GUI."""

import wx

from fitgirl_ddl_ng.extract_ddl import DEFAULT_SELECT_MARKERS


class GroupSelectDialog(wx.Dialog):
    def __init__(self, parent: wx.Window, slug: str, groups: list[str]) -> None:
        """
        Ask the user which download groups to keep for a game.

        :param parent: the parent window
        :param slug: the game slug shown in the title
        :param groups: the group names to choose from
        """

        super().__init__(parent, title=f"Select groups — {slug}", size=(520, 420))

        hint = wx.StaticText(self, label="Groups found for this game:")
        self.list = wx.CheckListBox(self, choices=groups)
        for index, group in enumerate(groups):
            if any(marker in group for marker in DEFAULT_SELECT_MARKERS):
                self.list.Check(index)

        buttons = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        self.Bind(wx.EVT_BUTTON, lambda _event: self.EndModal(wx.ID_OK), id=wx.ID_OK)
        self.Bind(
            wx.EVT_BUTTON,
            lambda _event: self.EndModal(wx.ID_CANCEL),
            id=wx.ID_CANCEL,
        )

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(hint, 0, wx.ALL, 8)
        sizer.Add(self.list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
        sizer.Add(buttons, 0, wx.EXPAND | wx.ALL, 8)
        self.SetSizer(sizer)

    def get_selection(self) -> list[str]:
        """
        Return the groups the user kept.

        :return: the selected group names
        """

        return [
            self.list.GetString(index)
            for index in range(self.list.GetCount())
            if self.list.IsChecked(index)
        ]
