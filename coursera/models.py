from dataclasses import dataclass


class CourseraApiModel:
    def __init__(self, data):
        fields = self.__class__.__dict__["__dataclass_fields__"].keys()
        for key in data:
            if key in fields:
                setattr(self, key, data[key])


@dataclass(init=False)
class User(CourseraApiModel):
    id: str
    name: str
    timezone: str
    locale: str
    privacy: int


@dataclass(init=False)
class LabImageConfig(CourseraApiModel):
    typeName: str
    imageAssetId: str
    httpPort: int
    healthCheckPath: str


@dataclass(init=False)
class LabImage(CourseraApiModel):
    id: str
    name: str
    description: str
    maxMemoryInMb: int
    maxCpus: float
    labImageConfig: LabImageConfig

    def __init__(self, data):
        self.id = data["id"]
        data["labImage"]["labImageConfig"] = LabImageConfig(
            data["labImage"]["labImageConfig"]
        )
        super().__init__(data["labImage"])


@dataclass(init=False)
class LabMountPoint(CourseraApiModel):
    mountPath: str
    isDeletable: bool
    isPathRenameable: bool
    isReadOnly: bool


@dataclass(init=False)
class Lab(CourseraApiModel):
    id: str
    name: str
    description: str
    labMountPoints: [LabMountPoint]

    def __init__(self, data):
        self.id = data["id"]
        data["lab"]["labMountPoints"] = [
            LabMountPoint(x) for x in data["lab"]["labMountPoints"]
        ]
        super().__init__(data["lab"])


@dataclass(init=False)
class ItemReference(CourseraApiModel):
    courseId: str
    branchId: str
    moduleId: str
    lessonId: str
    itemId: str
    itemType: str
