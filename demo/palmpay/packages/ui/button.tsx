import type { ComponentProps } from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

const buttonVariants = cva('', {
  variants: {
    variant: { default: 'primary', secondary: 'secondary', ghost: 'quiet', icon: 'icon-button' },
  },
  defaultVariants: { variant: 'default' },
})

export function Button({
  className, variant, asChild = false, ...props
}: ComponentProps<'button'> & VariantProps<typeof buttonVariants> & { asChild?: boolean }) {
  const Component = asChild ? Slot : 'button'
  return <Component data-slot="button" className={twMerge(clsx(buttonVariants({variant}), className))} {...props}/>
}

