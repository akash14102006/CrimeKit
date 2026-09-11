import * as React from "react"
import { Select as SelectPrimitive } from "@base-ui/react/select"

import { cn } from "@/lib/utils"
import { CheckIcon, ChevronDownIcon } from "lucide-react"

const Select = SelectPrimitive.Root
const SelectGroup = SelectPrimitive.Group
const SelectValue = SelectPrimitive.Value
const SelectLabel = SelectPrimitive.Label

function SelectTrigger({
  className,
  children,
  ...props
}: React.ComponentProps<typeof SelectPrimitive.Trigger>) {
  return (
    <SelectPrimitive.Trigger
      data-slot="select-trigger"
      className={cn(
        "flex h-8 w-full min-w-0 items-center justify-between gap-2 rounded-lg border border-input bg-transparent px-2.5 py-1 text-sm transition-colors outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 data-placeholder:text-muted-foreground",
        className
      )}
      {...props}
    >
      {children}
      <ChevronDownIcon
        className="size-4 shrink-0 text-muted-foreground"
        aria-hidden="true"
      />
    </SelectPrimitive.Trigger>
  )
}

function SelectPositioner({
  className,
  ...props
}: React.ComponentProps<typeof SelectPrimitive.Positioner>) {
  return (
    <SelectPrimitive.Positioner
      data-slot="select-positioner"
      className={cn(
        "z-50 min-w-[--anchor-width] rounded-lg border bg-popover text-popover-foreground shadow-md outline-none",
        className
      )}
      {...props}
    />
  )
}

function SelectPopup({
  className,
  ...props
}: React.ComponentProps<typeof SelectPrimitive.Popup>) {
  return (
    <SelectPrimitive.Popup
      data-slot="select-popup"
      className={cn("p-1", className)}
      {...props}
    />
  )
}

function SelectItem({
  className,
  children,
  ...props
}: React.ComponentProps<typeof SelectPrimitive.Item>) {
  return (
    <SelectPrimitive.Item
      data-slot="select-item"
      className={cn(
        "relative flex w-full cursor-default select-none items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none data-highlighted:bg-muted focus:outline-none",
        className
      )}
      {...props}
    >
      <span className="flex size-3.5 shrink-0 items-center justify-center">
        <SelectPrimitive.ItemIndicator>
          <CheckIcon className="size-3.5" aria-hidden="true" />
        </SelectPrimitive.ItemIndicator>
      </span>
      <SelectPrimitive.ItemText className="flex-1 truncate">
        {children}
      </SelectPrimitive.ItemText>
    </SelectPrimitive.Item>
  )
}

export {
  Select,
  SelectGroup,
  SelectValue,
  SelectLabel,
  SelectTrigger,
  SelectPositioner,
  SelectPopup,
  SelectItem,
}
