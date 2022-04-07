from typing import List, Optional
from pydantic import BaseModel


class Model(BaseModel):
    class Config:
        orm_mode = True


class User(Model):
    id: str
    name: str
    timezone: str
    locale: str
    privacy: int


class LabImageConfig(Model):
    typeName: str
    imageAssetId: str
    httpPort: int
    healthCheckPath: str


class LabImage(Model):
    id: str
    name: str
    description: Optional[str]
    maxMemoryInMb: int
    maxCpus: float
    labImageConfig: LabImageConfig


class LabMountPoint(Model):
    mountPath: str
    isDeletable: bool
    isPathRenamable: bool
    isReadOnly: bool


class Lab(Model):
    id: str
    name: str
    description: Optional[str]
    labMountPoints: List[LabMountPoint]


class ItemReference(Model):
    courseId: str
    branchId: str
    moduleId: str
    lessonId: str
    itemId: str
    itemType: str
