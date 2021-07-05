from System.IO import *

from Deadline.Scripting import *
from DeadlineUI.Controls.Scripting.DeadlineScriptDialog import DeadlineScriptDialog

########################################################################
## Globals
########################################################################
scriptDialog = None
settings = None

########################################################################
## Main Function Called By Deadline
########################################################################
def __main__():
    global scriptDialog
    global settings

    scriptDialog = DeadlineScriptDialog()
    scriptDialog.SetTitle("Script UI Example")

    scriptDialog.AddTabControl("Example Tab Control", 0, 0)

    scriptDialog.AddTabPage("Tab Page 1 : Deadline Controls")
    scriptDialog.AddGroupBox("GroupBox1", "Deadline Job Controls", True)
    scriptDialog.AddGrid()
    scriptDialog.AddControlToGrid(
        "Separator1", "SeparatorControl", "Job Description", 0, 0, colSpan=2
    )

    scriptDialog.AddControlToGrid(
        "NameLabel",
        "LabelControl",
        "Job Name",
        1,
        0,
        "The name of your job. This is optional, and if left blank, it will default to 'Untitled'.",
        False,
    )
    scriptDialog.AddControlToGrid("NameBox", "TextControl", "Untitled", 1, 1)

    scriptDialog.AddControlToGrid(
        "CommentLabel",
        "LabelControl",
        "Comment",
        2,
        0,
        "A simple description of your job. This is optional and can be left blank.",
        False,
    )
    scriptDialog.AddControlToGrid("CommentBox", "TextControl", "", 2, 1)

    scriptDialog.AddControlToGrid(
        "DepartmentLabel",
        "LabelControl",
        "Department",
        3,
        0,
        "The department you belong to. This is optional and can be left blank.",
        False,
    )
    scriptDialog.AddControlToGrid("DepartmentBox", "TextControl", "", 3, 1)
    scriptDialog.EndGrid()

    scriptDialog.AddGrid()
    scriptDialog.AddControlToGrid(
        "Separator2", "SeparatorControl", "Job Options", 0, 0, colSpan=3
    )

    scriptDialog.AddControlToGrid(
        "PoolLabel",
        "LabelControl",
        "Pool",
        1,
        0,
        "The pool that your job will be submitted to.",
        False,
    )
    scriptDialog.AddControlToGrid("PoolBox", "PoolComboControl", "none", 1, 1)

    scriptDialog.AddControlToGrid(
        "SecondaryPoolLabel",
        "LabelControl",
        "Secondary Pool",
        2,
        0,
        "The secondary pool lets you specify a Pool to use if the primary Pool does not have any available Workers.",
        False,
    )
    scriptDialog.AddControlToGrid(
        "SecondaryPoolBox", "SecondaryPoolComboControl", "", 2, 1
    )

    scriptDialog.AddControlToGrid(
        "GroupLabel",
        "LabelControl",
        "Group",
        3,
        0,
        "The group that your job will be submitted to.",
        False,
    )
    scriptDialog.AddControlToGrid("GroupBox", "GroupComboControl", "none", 3, 1)

    scriptDialog.AddControlToGrid(
        "PriorityLabel",
        "LabelControl",
        "Priority",
        4,
        0,
        "A job can have a numeric priority ranging from 0 to 100, where 0 is the lowest priority and 100 is the highest priority.",
        False,
    )
    scriptDialog.AddRangeControlToGrid(
        "PriorityBox",
        "RangeControl",
        RepositoryUtils.GetMaximumPriority() / 2,
        0,
        RepositoryUtils.GetMaximumPriority(),
        0,
        1,
        4,
        1,
    )

    scriptDialog.AddControlToGrid(
        "TaskTimeoutLabel",
        "LabelControl",
        "Task Timeout",
        5,
        0,
        "The number of minutes a Worker has to render a task for this job before it requeues it. Specify 0 for no limit.",
        False,
    )
    scriptDialog.AddRangeControlToGrid(
        "TaskTimeoutBox", "RangeControl", 0, 0, 1000000, 0, 1, 5, 1
    )
    scriptDialog.AddSelectionControlToGrid(
        "AutoTimeoutBox",
        "CheckBoxControl",
        False,
        "Enable Auto Task Timeout",
        5,
        2,
        "If the Auto Task Timeout is properly configured in the Repository Options, then enabling this will allow a task timeout to be automatically calculated based on the render times of previous frames for the job. ",
    )

    scriptDialog.AddControlToGrid(
        "ConcurrentTasksLabel",
        "LabelControl",
        "Concurrent Tasks",
        6,
        0,
        "The number of tasks that can render concurrently on a single Worker. This is useful if the rendering application only uses one thread to render and your Workers have multiple CPUs.",
        False,
    )
    scriptDialog.AddRangeControlToGrid(
        "ConcurrentTasksBox", "RangeControl", 1, 1, 16, 0, 1, 6, 1
    )
    scriptDialog.AddSelectionControlToGrid(
        "LimitConcurrentTasksBox",
        "CheckBoxControl",
        True,
        "Limit Tasks To Worker's Task Limit",
        6,
        2,
        "If you limit the tasks to a Worker's task limit, then by default, the Worker won't dequeue more tasks then it has CPUs. This task limit can be overridden for individual Workers by an administrator.",
    )

    scriptDialog.AddControlToGrid(
        "MachineLimitLabel",
        "LabelControl",
        "Machine Limit",
        7,
        0,
        "Use the Machine Limit to specify the maximum number of machines that can render your job at one time. Specify 0 for no limit.",
        False,
    )
    scriptDialog.AddRangeControlToGrid(
        "MachineLimitBox", "RangeControl", 0, 0, 1000000, 0, 1, 7, 1
    )
    scriptDialog.AddSelectionControlToGrid(
        "IsBlacklistBox",
        "CheckBoxControl",
        False,
        "Machine List Is A Blacklist",
        7,
        2,
        "You can force the job to render on specific machines by using a whitelist, or you can avoid specific machines by using a blacklist.",
    )

    scriptDialog.AddControlToGrid(
        "MachineListLabel",
        "LabelControl",
        "Machine List",
        8,
        0,
        "The whitelisted or blacklisted list of machines.",
        False,
    )
    scriptDialog.AddControlToGrid(
        "MachineListBox", "MachineListControl", "", 8, 1, colSpan=2
    )

    scriptDialog.AddControlToGrid(
        "LimitGroupLabel",
        "LabelControl",
        "Limits",
        9,
        0,
        "The Limits that your job requires.",
        False,
    )
    scriptDialog.AddControlToGrid(
        "LimitGroupBox", "LimitGroupControl", "", 9, 1, colSpan=2
    )

    scriptDialog.AddControlToGrid(
        "DependencyLabel",
        "LabelControl",
        "Dependencies",
        10,
        0,
        "Specify existing jobs that this job will be dependent on. This job will not start until the specified dependencies finish rendering.",
        False,
    )
    scriptDialog.AddControlToGrid(
        "DependencyBox", "DependencyControl", "", 10, 1, colSpan=2
    )

    scriptDialog.AddControlToGrid(
        "OnJobCompleteLabel",
        "LabelControl",
        "On Job Complete",
        11,
        0,
        "If desired, you can automatically archive or delete the job when it completes.",
        False,
    )
    scriptDialog.AddControlToGrid(
        "OnJobCompleteBox", "OnJobCompleteControl", "Nothing", 11, 1
    )
    scriptDialog.AddSelectionControlToGrid(
        "SubmitSuspendedBox",
        "CheckBoxControl",
        False,
        "Submit Job As Suspended",
        11,
        2,
        "If enabled, the job will submit in the suspended state. This is useful if you don't want the job to start rendering right away. Just resume it from the Monitor when you want it to render.",
    )
    scriptDialog.EndGrid()
    scriptDialog.EndGroupBox(False)
    scriptDialog.EndTabPage()

    scriptDialog.AddTabPage("Tab Page 2 : Simple Controls")
    scriptDialog.AddGroupBox("GroupBox2", "Other UI Controls", True)
    scriptDialog.AddGrid()

    scriptDialog.AddControlToGrid(
        "TextLabel", "LabelControl", "Enter Text Here", 0, 0, expand=False
    )
    scriptDialog.AddControlToGrid(
        "TextBox", "TextControl", "Some Text", 0, 1, colSpan=2
    )

    scriptDialog.AddControlToGrid(
        "ReadOnlyTextLabel", "LabelControl", "Read This Text", 1, 0, expand=False
    )
    scriptDialog.AddControlToGrid(
        "ReadOnlyTextBox", "ReadOnlyTextControl", "Some Read Only Text", 1, 1, colSpan=2
    )

    scriptDialog.AddControlToGrid(
        "MultiLineTextLabel", "LabelControl", "Multi Line", 2, 0, expand=False
    )
    scriptDialog.AddControlToGrid(
        "MultiLineTextBox",
        "MultiLineTextControl",
        "One Line\rAnother Line",
        2,
        1,
        "",
        colSpan=2,
    )

    scriptDialog.AddControlToGrid(
        "RangeLabel", "LabelControl", "Select A Number", 3, 0, expand=False
    )
    scriptDialog.AddRangeControlToGrid(
        "RangeBox", "RangeControl", 50.0, 0.0, 100.0, 1, 5.0, 3, 1
    )
    scriptDialog.AddSelectionControlToGrid(
        "CheckBox", "CheckBoxControl", False, "This is a Check Box", 3, 2
    )

    scriptDialog.AddControlToGrid(
        "SliderLabel", "LabelControl", "Select A Number", 4, 0, expand=False
    )
    scriptDialog.AddRangeControlToGrid(
        "SliderBox", "SliderControl", 50, 0, 100, 0, 1, 4, 1, colSpan=2
    )

    scriptDialog.AddControlToGrid(
        "ComboLabel", "LabelControl", "Select An Item", 5, 0, expand=False
    )
    scriptDialog.AddComboControlToGrid(
        "ComboBox",
        "ComboControl",
        "2008",
        ("2007", "2008", "2009", "2010", "2011"),
        5,
        1,
    )
    scriptDialog.AddControlToGrid(
        "LinkLabel",
        "LabelControl",
        '<a href="http://www.thinkboxsoftware.com">www.thinkboxsoftware.com</a>',
        5,
        2,
    )

    scriptDialog.AddControlToGrid(
        "ColorLabel", "LabelControl", "Select A Color", 6, 0, expand=False
    )
    scriptDialog.AddControlToGrid(
        "ColorBox", "ColorControl", scriptDialog.CreateColorObject(255, 0, 0), 6, 1
    )

    scriptDialog.AddControlToGrid(
        "ProgressLabel", "LabelControl", "Progress", 7, 0, expand=False
    )
    scriptDialog.AddRangeControlToGrid(
        "ProgressBox", "ProgressBarControl", 1, 1, 100, 0, 0, 7, 1
    )
    progressButton = scriptDialog.AddControlToGrid(
        "ProgressButton", "ButtonControl", "Increment", 7, 2
    )
    progressButton.ValueModified.connect(ProgressButtonPressed)
    scriptDialog.EndGrid()

    scriptDialog.AddGrid()
    scriptDialog.AddRadioControlToGrid(
        "RadioOne", "RadioControl", True, "Radio One", "RadioGroup", 0, 0
    )
    scriptDialog.AddRadioControlToGrid(
        "RadioTwo", "RadioControl", False, "Radio Two", "RadioGroup", 0, 1
    )
    scriptDialog.AddRadioControlToGrid(
        "RadioThree", "RadioControl", False, "Radio Three", "RadioGroup", 0, 2
    )
    scriptDialog.AddRadioControlToGrid(
        "RadioFour", "RadioControl", False, "Radio Four", "RadioGroup", 0, 3
    )
    scriptDialog.EndGrid()
    scriptDialog.EndGroupBox(False)
    scriptDialog.EndTabPage()

    scriptDialog.AddTabPage("Tab Page 3 : Browsers")
    scriptDialog.AddGrid()
    scriptDialog.AddControlToGrid(
        "Separator3", "SeparatorControl", "Browsers", 0, 0, colSpan=2
    )

    scriptDialog.AddControlToGrid(
        "FolderLabel", "LabelControl", "Select Folder", 1, 0, expand=False
    )
    scriptDialog.AddSelectionControlToGrid(
        "FolderBox", "FolderBrowserControl", "", "", 1, 1
    )

    scriptDialog.AddControlToGrid(
        "FileLabel", "LabelControl", "Select File", 2, 0, expand=False
    )
    # File Filter demonstrates how to control the file formats to be selected - Text or All Files
    scriptDialog.AddSelectionControlToGrid(
        "FileBox", "FileBrowserControl", "", "Text Files (*.txt);;All Files (*.*)", 2, 1
    )

    scriptDialog.AddControlToGrid(
        "SaveFileLabel", "LabelControl", "Save File", 3, 0, expand=False
    )
    # File Filter demonstrates how to control the file formats to be selected - Text or All Files
    scriptDialog.AddSelectionControlToGrid(
        "SaveFileBox",
        "FileSaverControl",
        "",
        "Text Files (*.txt);;All Files (*.*)",
        3,
        1,
    )

    scriptDialog.AddControlToGrid(
        "MultiFileLabel", "LabelControl", "Multi File", 4, 0, expand=False
    )
    scriptDialog.AddSelectionControlToGrid(
        "MultiFileBox", "MultiFileBrowserControl", "", "All Files (*.*)", 4, 1
    )

    scriptDialog.AddControlToGrid(
        "MultiLineFolderLabel", "LabelControl", "Multi Line Folder", 5, 0, expand=False
    )
    scriptDialog.AddSelectionControlToGrid(
        "MultiLineFolderBox", "MultiLineMultiFolderBrowserControl", "", "", 5, 1
    )

    scriptDialog.AddControlToGrid(
        "MultiLineFileLabel", "LabelControl", "Multi Line File", 6, 0, expand=False
    )
    scriptDialog.AddSelectionControlToGrid(
        "MultiLineFileBox",
        "MultiLineMultiFileBrowserControl",
        "",
        "All Files (*.*)",
        6,
        1,
    )
    scriptDialog.EndGrid()

    scriptDialog.EndTabPage()
    scriptDialog.EndTabControl()

    scriptDialog.AddGrid()
    dialogButton = scriptDialog.AddControlToGrid(
        "DialogButton", "ButtonControl", "Dialog", 0, 0, expand=False
    )
    dialogButton.ValueModified.connect(DialogButtonPressed)
    popupButton = scriptDialog.AddControlToGrid(
        "PopupButton", "ButtonControl", "Popup", 0, 1, expand=False
    )
    popupButton.ValueModified.connect(PopupButtonPressed)
    closeButton = scriptDialog.AddControlToGrid(
        "CloseButton", "ButtonControl", "Close", 0, 2, expand=False
    )
    closeButton.ValueModified.connect(CloseButtonPressed)
    scriptDialog.AddHorizontalSpacerToGrid("DummySpacer1", 0, 3)
    scriptDialog.EndGrid()

    scriptDialog.ShowDialog(True)


########################################################################
## Helper Functions
########################################################################
def DialogButtonPressed(*args):
    global scriptDialog

    newDialog = DeadlineScriptDialog()

    newDialog.SetSize(350, 0)
    newDialog.SetTitle("Another Window!")

    newDialog.AddGrid()
    newDialog.AddControlToGrid(
        "Separator1", "SeparatorControl", "Simple Controls", 0, 0, colSpan=2
    )

    newDialog.AddControlToGrid(
        "TextLabel", "LabelControl", "Enter Text Here", 1, 0, expand=False
    )
    newDialog.AddControlToGrid("TextBox", "TextControl", "Some Text", 1, 1)

    newDialog.AddControlToGrid(
        "ReadOnlyTextLabel", "LabelControl", "Read Only Text", 2, 0, expand=False
    )
    newDialog.AddControlToGrid(
        "ReadOnlyTextBox", "ReadOnlyTextControl", "Some Read Only Text", 2, 1
    )
    newDialog.EndGrid()

    newDialog.ShowDialog(True)


def ProgressButtonPressed(*args):
    global scriptDialog

    currentProgress = scriptDialog.GetValue("ProgressBox")
    currentProgress = currentProgress + 5
    if currentProgress > 100:
        currentProgress = 1
    scriptDialog.SetValue("ProgressBox", currentProgress)


def CloseButtonPressed(*args):
    global scriptDialog
    scriptDialog.CloseDialog()


def PopupButtonPressed(*args):
    global scriptDialog
    scriptDialog.ShowMessageBox("This is a popup!", "Popup")
